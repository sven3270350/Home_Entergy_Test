import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Line } from 'react-chartjs-2';

interface ChatResponse {
  answer: string;
  data: {
    stats?: {
      avg_energy_watts: number;
      max_energy_watts: number;
      min_energy_watts: number;
      total_energy_watt_hours: number;
    };
    telemetry?: Array<{
      timestamp: string;
      energy_watts: number;
    }>;
  };
  device_id?: number;
  time_period?: string;
}

const CHAT_API_URL = process.env.REACT_APP_CHAT_API_URL || 'http://localhost:8002';

const Chat: React.FC = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { token } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(
        `${CHAT_API_URL}/api/chat/query`,
        {
          text: query,
          auth_token: token,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setResponse(response.data);
      setQuery('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get response');
    } finally {
      setIsLoading(false);
    }
  };

  const getChartData = () => {
    if (!response?.data?.telemetry) return null;

    return {
      labels: response.data.telemetry.map((d) =>
        new Date(d.timestamp).toLocaleTimeString()
      ),
      datasets: [
        {
          label: 'Energy Usage (Watts)',
          data: response.data.telemetry.map((d) => d.energy_watts),
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1,
        },
      ],
    };
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Ask about your energy usage
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Example questions:
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          • How much energy did my fridge use yesterday?
          <br />
          • Which device consumed the most power last week?
          <br />• What's my total energy consumption today?
        </Typography>

        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your question here..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
          />
          <Button
            type="submit"
            variant="contained"
            endIcon={<SendIcon />}
            sx={{ mt: 2 }}
            disabled={isLoading || !query.trim()}
          >
            Ask
          </Button>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {isLoading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}

      {response && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="body1" gutterBottom>
            {response.answer}
          </Typography>

          {response.data.stats && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Statistics
              </Typography>
              <Box display="flex" gap={4}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Average Power
                  </Typography>
                  <Typography variant="h6">
                    {response.data.stats.avg_energy_watts.toFixed(1)} W
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Maximum Power
                  </Typography>
                  <Typography variant="h6">
                    {response.data.stats.max_energy_watts.toFixed(1)} W
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Total Energy
                  </Typography>
                  <Typography variant="h6">
                    {(response.data.stats.total_energy_watt_hours / 1000).toFixed(2)} kWh
                  </Typography>
                </Box>
              </Box>
            </Box>
          )}

          {response.data.telemetry && (
            <Box sx={{ mt: 3, height: 300 }}>
              <Typography variant="h6" gutterBottom>
                Energy Usage Over Time
              </Typography>
              <Line
                data={getChartData()!}
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
          )}
        </Paper>
      )}
    </Container>
  );
};

export default Chat; 