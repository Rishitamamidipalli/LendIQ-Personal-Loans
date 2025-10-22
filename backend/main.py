from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
import sys
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import tempfile
import shutil
import io

# Add parent directory to path to import orchestration_agent
sys.path.append(str(Path(__file__).parent.parent))

from orchestration_strands import VerificationOrchestrator

# Helper function to make objects JSON serializable
def make_serializable(obj):
    """Convert any object to JSON-serializable format"""
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif hasattr(obj, '__dict__'):
        # For objects with __dict__ (like AgentResult)
        return make_serializable(obj.__dict__)
    elif hasattr(obj, 'to_dict'):
        # For objects with to_dict method
        return make_serializable(obj.to_dict())
    else:
        # Convert anything else to string
        return str(obj)

# S3 Configuration
S3_BUCKET_NAME = "documents-loaniq"
s3_client = boto3.client('s3')

# Helper functions for S3 operations
def download_json_from_s3(key: str) -> list:
    """Download and parse JSON file from S3"""
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return []  # Return empty list if file doesn't exist
        raise

def upload_json_to_s3(key: str, data: list):
    """Upload JSON data to S3"""
    json_content = json.dumps(data, indent=2)
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=json_content.encode('utf-8'),
        ContentType='application/json'
    )

def download_customer_folder_from_s3(customer_id: str, local_path: str):
    """Download all files for a customer from S3 to local temp directory"""
    prefix = f"{customer_id}/"
    
    # List all objects with the customer_id prefix
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=prefix)
    
    if 'Contents' not in response:
        raise HTTPException(status_code=404, detail=f"No documents found for customer {customer_id}")
    
    # Create local directory
    os.makedirs(local_path, exist_ok=True)
    
    # Download each file
    for obj in response['Contents']:
        key = obj['Key']
        if key == prefix:  # Skip the folder itself
            continue
        
        # Skip gradcam images (they're generated outputs, not inputs)
        if '/gradcam/' in key or '/offer_letter_gradcam/' in key:
            print(f"⏭️  Skipping GradCAM image: {key}")
            continue
        
        # Get filename from key
        filename = key.replace(prefix, '')
        local_file_path = os.path.join(local_path, filename)
        
        # Create subdirectories if needed
        local_file_dir = os.path.dirname(local_file_path)
        if local_file_dir:
            os.makedirs(local_file_dir, exist_ok=True)
        
        # Download file
        s3_client.download_file(S3_BUCKET_NAME, key, local_file_path)
        print(f"📥 Downloaded: {key} -> {local_file_path}")

def upload_results_to_s3(customer_id: str, results: dict):
    """Upload results.json to S3 for a customer"""
    key = f"{customer_id}/results.json"
    json_content = json.dumps(results, indent=2)
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=json_content.encode('utf-8'),
        ContentType='application/json'
    )
    print(f"📤 Uploaded results to S3: {key}")

app = FastAPI(title="Loan Verification API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WorkflowRequest(BaseModel):
    customer_id: str

class WorkflowResponse(BaseModel):
    status: str
    results: dict
    errors: list

@app.get("/")
async def root():
    return {"message": "Loan Verification API is running"}

@app.get("/customers")
async def get_customers():
    """Get all customer IDs from new_applications.json in S3"""
    try:
        customers = download_json_from_s3("new_applications.json")
        return {"customers": customers}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading customers from S3: {str(e)}")

@app.post("/run_workflow", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest):
    """Run the verification workflow for a specific customer"""
    temp_dir = None
    try:
        customer_id = request.customer_id
        
        # Validate customer_id exists in S3
        customers = download_json_from_s3("new_applications.json")
        
        if customer_id not in customers:
            raise HTTPException(status_code=404, detail=f"Customer ID {customer_id} not found")
        
        # Create temporary directory for customer documents
        temp_dir = tempfile.mkdtemp(prefix=f"customer_{customer_id}_")
        documents_folder = os.path.join(temp_dir, customer_id)
        
        print(f"🚀 Starting workflow for customer: {customer_id}")
        print(f"📥 Downloading documents from S3...")
        
        # Download customer documents from S3
        download_customer_folder_from_s3(customer_id, documents_folder)
        
        # Run the orchestration workflow
        print(f"⚙️ Running verification workflow...")
        orchestrator = VerificationOrchestrator(documents_folder)
        results = orchestrator.run_workflow()
        
        # Convert results to JSON-serializable format
        serializable_results = make_serializable(results)
        
        # Prepare results for UI
        ui_results = {
            "status": serializable_results.get("status", "unknown"),
            "errors": serializable_results.get("errors", []),
            "results": serializable_results.get("results", {})
        }
        
        # Upload results to S3
        upload_results_to_s3(customer_id, ui_results)
        
        print(f"✅ Workflow completed for customer: {customer_id}")
        
        # ⚠️ CHANGED: Return dummy_results.json from S3 instead of real results
        try:
            dummy_key = f"{customer_id}/dummy_results.json"
            dummy_response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=dummy_key)
            dummy_content = dummy_response['Body'].read().decode('utf-8')
            dummy_results = json.loads(dummy_content)
            
            print(f"📥 Returning dummy results from S3: {dummy_key}")
            
            return WorkflowResponse(
                status=dummy_results.get("status", "unknown"),
                results=dummy_results.get("results", {}),
                errors=dummy_results.get("errors", [])
            )
        except ClientError as e:
            # Fallback to real results if dummy file not found
            print(f"⚠️ Dummy results not found, returning real results")
            return WorkflowResponse(
                status=serializable_results.get("status", "unknown"),
                results=serializable_results.get("results", {}),
                errors=serializable_results.get("errors", [])
            )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Error in workflow: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up temporary directory")

@app.get("/results/{customer_id}")
async def get_results(customer_id: str):
    """Get saved results for a specific customer from S3"""
    try:
        #key=f"{customer_id}/results.json"
        # Changed to dummy_results.json to display dummy data in UI
        key = f"{customer_id}/dummy_results.json"
        
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
            content = response['Body'].read().decode('utf-8')
            results = json.loads(content)
            return results
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise HTTPException(
                    status_code=404, 
                    detail=f"Dummy results not found for customer {customer_id}. Please upload dummy_results.json first."
                )
            raise
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading results from S3: {str(e)}")

@app.get("/gradcam/{customer_id}/{filename}")
async def get_gradcam_image(customer_id: str, filename: str):
    """Download GradCAM image from S3"""
    try:
        # Construct S3 key - support both old and new paths
        s3_key = f"{customer_id}/gradcam/{filename}"
        
        # Try new path first, then fall back to old path
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                # Try old path
                s3_key = f"{customer_id}/offer_letter_gradcam/{filename}"
                response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            else:
                raise
        
        # Read image data
        image_data = response['Body'].read()
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(image_data),
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename={filename}"
            }
        )
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            raise HTTPException(
                status_code=404,
                detail=f"GradCAM image not found: {filename}"
            )
        raise HTTPException(status_code=500, detail=f"Error downloading image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading image: {str(e)}")

# Action endpoints
class ActionRequest(BaseModel):
    customer_id: str

@app.post("/send_email")
async def send_email(request: ActionRequest):
    """Send email notification to customer"""
    try:
        customer_id = request.customer_id
        
        # TODO: Implement actual email sending logic
        # For now, just log the action
        print(f"📧 Sending email to customer: {customer_id}")
        
        # You can add email service integration here (SendGrid, AWS SES, etc.)
        
        return {
            "status": "success",
            "message": f"Email sent to customer {customer_id}",
            "customer_id": customer_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@app.post("/send_sms")
async def send_sms(request: ActionRequest):
    """Send SMS notification to customer"""
    try:
        customer_id = request.customer_id
        
        # TODO: Implement actual SMS sending logic
        # For now, just log the action
        print(f"📱 Sending SMS to customer: {customer_id}")
        
        # You can add SMS service integration here (Twilio, AWS SNS, etc.)
        
        return {
            "status": "success",
            "message": f"SMS sent to customer {customer_id}",
            "customer_id": customer_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")

@app.post("/escalate")
async def escalate_to_human(request: ActionRequest):
    """Escalate case to human verification team"""
    try:
        customer_id = request.customer_id
        
        # Load existing escalations from S3
        escalations = download_json_from_s3("human_escalation.json")
        
        # Add customer to escalation list if not already there
        if customer_id not in escalations:
            escalations.append(customer_id)
            
            # Save to S3
            upload_json_to_s3("human_escalation.json", escalations)
            
            # Remove from new_applications.json in S3
            new_applications = download_json_from_s3("new_applications.json")
            
            if customer_id in new_applications:
                new_applications.remove(customer_id)
                upload_json_to_s3("new_applications.json", new_applications)
                
                print(f"⚠️ Customer {customer_id} escalated to human verification and removed from new applications")
            
            return {
                "status": "success",
                "message": f"Case escalated to human review for customer {customer_id}",
                "customer_id": customer_id
            }
        else:
            return {
                "status": "info",
                "message": f"Customer {customer_id} already in escalation queue",
                "customer_id": customer_id
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to escalate: {str(e)}")

@app.post("/approve_loan")
async def approve_loan(request: ActionRequest):
    """Approve loan for customer"""
    try:
        customer_id = request.customer_id
        
        # Load existing approvals from S3
        approvals = download_json_from_s3("approved_loans.json")
        
        # Add customer to approval list if not already there
        if customer_id not in approvals:
            approvals.append(customer_id)
            
            # Save to S3
            upload_json_to_s3("approved_loans.json", approvals)
            
            # Remove from new_applications.json in S3
            new_applications = download_json_from_s3("new_applications.json")
            
            if customer_id in new_applications:
                new_applications.remove(customer_id)
                upload_json_to_s3("new_applications.json", new_applications)
                
                print(f"✅ Loan approved for customer: {customer_id} and removed from new applications")
            
            return {
                "status": "success",
                "message": f"Loan approved for customer {customer_id}",
                "customer_id": customer_id
            }
        else:
            return {
                "status": "info",
                "message": f"Loan already approved for customer {customer_id}",
                "customer_id": customer_id
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve loan: {str(e)}")

@app.get("/approved-loans")
async def get_approved_loans():
    """Get list of approved loan IDs from S3"""
    try:
        approved_loans = download_json_from_s3("approved_loans.json")
        return {"approved_loans": approved_loans}
    except Exception as e:
        print(f"Error fetching approved loans: {str(e)}")
        return {"approved_loans": []}

@app.get("/human-escalations")
async def get_human_escalations():
    """Get list of escalated loan IDs from S3"""
    try:
        escalations = download_json_from_s3("human_escalation.json")
        return {"escalations": escalations}
    except Exception as e:
        print(f"Error fetching escalations: {str(e)}")
        return {"escalations": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
