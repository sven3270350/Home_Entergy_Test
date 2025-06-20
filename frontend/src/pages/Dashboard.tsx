import React, { useEffect, useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Box,
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface Device {
  id: number;
  name: string;
  device_type: string;
}

interface TelemetryData {
  timestamp: string;
  energy_watts: number;
}

interface DeviceStats {
  avg_energy_watts: number;
  max_energy_watts: number;
  min_energy_watts: number;
  total_energy_watt_hours: number;
}

const TELEMETRY_API_URL = process.env.REACT_APP_TELEMETRY_API_URL || 'http://localhost:8001';

const Dashboard: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [deviceStats, setDeviceStats] = useState<{ [key: number]: DeviceStats }>({});
  const [telemetryData, setTelemetryData] = useState<{ [key: number]: TelemetryData[] }>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch devices
        const devicesResponse = await axios.get(`${TELEMETRY_API_URL}/api/devices`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const fetchedDevices = devicesResponse.data;
        setDevices(fetchedDevices);

        // Fetch stats and telemetry for each device
        const statsPromises = fetchedDevices.map((device: Device) =>
          axios.get(`${TELEMETRY_API_URL}/api/telemetry/${device.id}/stats`, {
            headers: { Authorization: `Bearer ${token}` },
            params: { period: '24h' },
          })
        );

        const telemetryPromises = fetchedDevices.map((device: Device) =>
          axios.get(`${TELEMETRY_API_URL}/api/telemetry/${device.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          })
        );

        const statsResponses = await Promise.all(statsPromises);
        const telemetryResponses = await Promise.all(telemetryPromises);

        const newDeviceStats: { [key: number]: DeviceStats } = {};
        const newTelemetryData: { [key: number]: TelemetryData[] } = {};

        fetchedDevices.forEach((device: Device, index: number) => {
          newDeviceStats[device.id] = statsResponses[index].data;
          newTelemetryData[device.id] = telemetryResponses[index].data;
        });

        setDeviceStats(newDeviceStats);
        setTelemetryData(newTelemetryData);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to fetch data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [token]);

  const getChartData = (deviceId: number) => {
    const data = telemetryData[deviceId] || [];
    return {
      labels: data.map((d) => new Date(d.timestamp).toLocaleTimeString()),
      datasets: [
        {
          label: 'Energy Usage (Watts)',
          data: data.map((d) => d.energy_watts),
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1,
        },
      ],
    };
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Typography color="error" variant="h6" sx={{ mt: 4 }}>
          {error}
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {devices.map((device) => (
          <Grid item xs={12} md={6} key={device.id}>
            <Paper
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                height: 400,
              }}
            >
              <Typography component="h2" variant="h6" color="primary" gutterBottom>
                {device.name}
              </Typography>
              <Box sx={{ flex: 1, minHeight: 200 }}>
                <Line
                  data={getChartData(device.id)}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top' as const,
                      },
                    },
                  }}
                />
              </Box>
              <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Average Power:
                  </Typography>
                  <Typography variant="h6">
                    {deviceStats[device.id]?.avg_energy_watts.toFixed(1)} W
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Energy:
                  </Typography>
                  <Typography variant="h6">
                    {(deviceStats[device.id]?.total_energy_watt_hours / 1000).toFixed(2)} kWh
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Dashboard; 