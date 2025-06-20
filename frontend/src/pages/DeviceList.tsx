import React, { useEffect, useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  CircularProgress,
  Box,
  Alert,
} from '@mui/material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface Device {
  id: number;
  name: string;
  device_type: string;
}

const deviceTypes = [
  'Refrigerator',
  'Air Conditioner',
  'Washing Machine',
  'Dishwasher',
  'Water Heater',
  'Light',
  'TV',
  'Computer',
  'Other',
];

const TELEMETRY_API_URL = process.env.REACT_APP_TELEMETRY_API_URL || 'http://localhost:8001';

const DeviceList: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [newDevice, setNewDevice] = useState({
    name: '',
    device_type: '',
  });
  const { token } = useAuth();

  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${TELEMETRY_API_URL}/api/devices`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setDevices(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch devices');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, [token]);

  const handleAddDevice = async () => {
    try {
      await axios.post(
        `${TELEMETRY_API_URL}/api/devices`,
        newDevice,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setOpenDialog(false);
      setNewDevice({ name: '', device_type: '' });
      fetchDevices();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add device');
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4">Your Devices</Typography>
        <Button variant="contained" onClick={() => setOpenDialog(true)}>
          Add Device
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {devices.map((device) => (
          <Grid item xs={12} sm={6} md={4} key={device.id}>
            <Paper
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
              }}
            >
              <Typography variant="h6" gutterBottom>
                {device.name}
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 2 }}>
                Type: {device.device_type}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Device ID: {device.id}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Add New Device</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Device Name"
            fullWidth
            value={newDevice.name}
            onChange={(e) => setNewDevice({ ...newDevice, name: e.target.value })}
          />
          <TextField
            select
            margin="dense"
            label="Device Type"
            fullWidth
            value={newDevice.device_type}
            onChange={(e) => setNewDevice({ ...newDevice, device_type: e.target.value })}
          >
            {deviceTypes.map((type) => (
              <MenuItem key={type} value={type}>
                {type}
              </MenuItem>
            ))}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleAddDevice} variant="contained">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default DeviceList; 