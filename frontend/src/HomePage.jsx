import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Avatar,
  Paper,
} from '@mui/material';
import {
  AccountBalance as BankIcon,
  Description as FormIcon,
  Assessment as ResultsIcon,
  People as PeopleIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  CreditCard as CreditCardIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';

const HomePage = ({ onNavigateToApp, onNavigateToEscalations, onNavigateToApprovedLoans }) => {
  // Dashboard counters
  const dashboardStats = [
    {
      icon: <PeopleIcon sx={{ fontSize: 40 }} />,
      title: "New Applicants",
      value: "5",
      color: '#1976d2',
      description: "Active applications",
      onClick: onNavigateToApp
    },
    {
      icon: <WarningIcon sx={{ fontSize: 40 }} />,
      title: "Human Escalation",
      value: "2",
      color: '#ed6c02',
      description: "Requires review",
      onClick: onNavigateToEscalations
    },
    {
      icon: <CheckCircleIcon sx={{ fontSize: 40 }} />,
      title: "Approved Loans",
      value: "756",
      color: '#2e7d32',
      description: "Loans approved",
      onClick: onNavigateToApprovedLoans
    }
  ];

  const features = [
    {
      icon: <AssignmentIcon sx={{ fontSize: 40 }} />,
      title: "Application Review",
      description: "Review and process loan applications with our AI-powered verification system.",
      action: "Review Applications",
      onClick: onNavigateToApp,
      color: '#1976d2'
    },
    {
      icon: <FormIcon sx={{ fontSize: 40 }} />,
      title: "Document Verification",
      description: "AI-powered document analysis to detect manipulation and verify authenticity.",
      action: "Verify Documents",
      onClick: onNavigateToApp,
      color: '#2e7d32'
    },
    {
      icon: <ResultsIcon sx={{ fontSize: 40 }} />,
      title: "Risk Assessment",
      description: "Comprehensive risk analysis and loan eligibility recommendations.",
      action: "View Analytics",
      onClick: onNavigateToApp,
      color: '#0288d1'
    }
  ];

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Hero Section */}
      <Box sx={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        py: 8,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <Container maxWidth="xl">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h2" component="h1" sx={{ 
                fontWeight: 700,
                mb: 3,
                lineHeight: 1.2
              }}>
                LendIQ
                <br />
                <span style={{ color: '#90caf9' }}>Loan Verification System</span>
              </Typography>
              <Typography variant="h5" sx={{ 
                mb: 4,
                opacity: 0.9,
                fontWeight: 300
              }}>
                AI-Powered Document Verification & Risk Assessment for Personal Loan Applications
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<AssignmentIcon />}
                  onClick={onNavigateToApp}
                  sx={{
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    borderRadius: 3,
                    bgcolor: 'white',
                    color: '#667eea',
                    boxShadow: 3,
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: 6,
                      bgcolor: '#f5f5f5',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  View Applications
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  startIcon={<FormIcon />}
                  onClick={onNavigateToApp}
                  sx={{
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                    borderRadius: 3,
                    borderColor: 'white',
                    color: 'white',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      borderColor: 'white',
                      bgcolor: 'rgba(255,255,255,0.1)',
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  Get Started
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={6} sx={{ textAlign: 'center' }}>
              <Avatar sx={{ 
                width: 200, 
                height: 200, 
                mx: 'auto',
                backgroundColor: 'rgba(255,255,255,0.2)',
                border: '4px solid rgba(255,255,255,0.3)'
              }}>
                <BankIcon sx={{ fontSize: 100 }} />
              </Avatar>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Dashboard Counters Section */}
      <Container maxWidth="xl" sx={{ py: 6 }}>
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h3" component="h2" sx={{ 
            fontWeight: 600,
            mb: 2,
            color: '#333'
          }}>
            Loan Portfolio Overview
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            Real-time statistics of loan applications and processing status
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {dashboardStats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card 
                sx={{ 
                  height: '100%',
                  textAlign: 'center',
                  p: 3,
                  transition: 'all 0.3s ease',
                  cursor: stat.onClick ? 'pointer' : 'default',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 24px rgba(0,0,0,0.15)'
                  }
                }}
                onClick={stat.onClick}
              >
                <Avatar sx={{ 
                  width: 80, 
                  height: 80, 
                  mx: 'auto', 
                  mb: 3,
                  bgcolor: stat.color
                }}>
                  {stat.icon}
                </Avatar>
                <Typography variant="h2" component="div" sx={{ 
                  fontWeight: 700,
                  mb: 1,
                  color: stat.color
                }}>
                  {stat.value}
                </Typography>
                <Typography variant="h6" component="h3" sx={{ 
                  fontWeight: 600,
                  mb: 1
                }}>
                  {stat.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {stat.description}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Features Section */}
      <Box sx={{ bgcolor: 'white', py: 8 }}>
        <Container maxWidth="xl">
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Typography variant="h3" component="h2" sx={{ 
              fontWeight: 600,
              mb: 2,
              color: '#333'
            }}>
              Platform Features
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
              Comprehensive tools for efficient loan processing and risk management
            </Typography>
          </Box>

          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card sx={{ 
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: '0 12px 24px rgba(0,0,0,0.15)'
                  }
                }}>
                  <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 4 }}>
                    <Avatar sx={{ 
                      width: 70, 
                      height: 70, 
                      mx: 'auto', 
                      mb: 3,
                      bgcolor: feature.color
                    }}>
                      {feature.icon}
                    </Avatar>
                    <Typography variant="h5" component="h3" sx={{ 
                      fontWeight: 600,
                      mb: 2
                    }}>
                      {feature.title}
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                      {feature.description}
                    </Typography>
                    <Button
                      variant="contained"
                      onClick={feature.onClick}
                      sx={{
                        bgcolor: feature.color,
                        '&:hover': {
                          bgcolor: feature.color,
                          opacity: 0.9
                        }
                      }}
                    >
                      {feature.action}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ bgcolor: '#333', color: 'white', py: 4, mt: 8 }}>
        <Container maxWidth="xl">
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                LendIQ
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                AI-Powered Loan Verification System
              </Typography>
            </Grid>
            <Grid item xs={12} md={6} sx={{ textAlign: { xs: 'left', md: 'right' } }}>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                © 2025 LendIQ. All rights reserved.
              </Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default HomePage;
