<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Exception;

class TradingBotController extends Controller
{
    /**
     * Backend API URL
     */
    private string $backendUrl;

    public function __construct()
    {
        $this->backendUrl = env('BACKEND_URL', 'http://localhost:8080');
    }

    /**
     * Start the autonomous trading bot
     */
    public function start(Request $request): JsonResponse
    {
        try {
            $response = Http::timeout(30)->post("{$this->backendUrl}/start");
            
            if ($response->successful()) {
                $data = $response->json();
                Log::info('Trading bot started successfully', $data);
                
                return response()->json([
                    'success' => true,
                    'message' => 'Trading bot started successfully',
                    'data' => $data
                ]);
            }
            
            Log::error('Failed to start trading bot', ['response' => $response->body()]);
            return response()->json([
                'success' => false,
                'message' => 'Failed to start trading bot',
                'error' => $response->body()
            ], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error starting trading bot', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => false,
                'message' => 'Error communicating with trading bot',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Stop the autonomous trading bot
     */
    public function stop(Request $request): JsonResponse
    {
        try {
            $response = Http::timeout(30)->post("{$this->backendUrl}/stop");
            
            if ($response->successful()) {
                $data = $response->json();
                Log::info('Trading bot stopped successfully', $data);
                
                return response()->json([
                    'success' => true,
                    'message' => 'Trading bot stopped successfully',
                    'data' => $data
                ]);
            }
            
            Log::error('Failed to stop trading bot', ['response' => $response->body()]);
            return response()->json([
                'success' => false,
                'message' => 'Failed to stop trading bot',
                'error' => $response->body()
            ], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error stopping trading bot', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => false,
                'message' => 'Error communicating with trading bot',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get current trading status
     */
    public function status(): JsonResponse
    {
        try {
            $response = Http::timeout(10)->get("{$this->backendUrl}/status");
            
            if ($response->successful()) {
                $data = $response->json();
                
                return response()->json([
                    'success' => true,
                    'data' => $data
                ]);
            }
            
            return response()->json([
                'success' => false,
                'message' => 'Failed to get status',
                'error' => $response->body()
            ], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error getting trading bot status', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => false,
                'message' => 'Error communicating with trading bot',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Switch between paper and live trading modes
     */
    public function switchMode(Request $request): JsonResponse
    {
        $request->validate([
            'mode' => 'required|string|in:paper,live'
        ]);

        try {
            $response = Http::timeout(30)->post("{$this->backendUrl}/switch-mode", [
                'mode' => $request->mode
            ]);
            
            if ($response->successful()) {
                $data = $response->json();
                Log::info('Trading mode switched', $data);
                
                return response()->json([
                    'success' => true,
                    'message' => "Switched to {$request->mode} mode",
                    'data' => $data
                ]);
            }
            
            Log::error('Failed to switch trading mode', ['response' => $response->body()]);
            return response()->json([
                'success' => false,
                'message' => 'Failed to switch trading mode',
                'error' => $response->body()
            ], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error switching trading mode', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => false,
                'message' => 'Error communicating with trading bot',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Configure trading stocks
     */
    public function configure(Request $request): JsonResponse
    {
        $request->validate([
            'stocks' => 'required|array|min:1',
            'stocks.*' => 'required|string|max:10'
        ]);

        try {
            $response = Http::timeout(30)->post("{$this->backendUrl}/configure", [
                'stocks' => $request->stocks
            ]);
            
            if ($response->successful()) {
                $data = $response->json();
                Log::info('Trading stocks configured', $data);
                
                return response()->json([
                    'success' => true,
                    'message' => 'Stock configuration updated',
                    'data' => $data
                ]);
            }
            
            Log::error('Failed to configure stocks', ['response' => $response->body()]);
            return response()->json([
                'success' => false,
                'message' => 'Failed to configure stocks',
                'error' => $response->body()
            ], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error configuring stocks', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => false,
                'message' => 'Error communicating with trading bot',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Evaluate a specific agent
     */
    public function evaluate(Request $request, string $symbol): JsonResponse
    {
        try {
            $response = Http::timeout(30)->get("{$this->backendUrl}/evaluate/{$symbol}");
            
            if ($response->successful()) {
                $data = $response->json();
                
                return response()->json([
                    'success' => true,
                    'data' => $data
                ]);
            }
            
            return response()->json([
                'success' => false,
                'message' => 'Failed to evaluate agent',
                'error' => $response->body()
            ], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error evaluating agent', ['symbol' => $symbol, 'error' => $e->getMessage()]);
            return response()->json([
                'success' => false,
                'message' => 'Error communicating with trading bot',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Retrain a specific agent
     */
    public function retrain(Request $request, string $symbol): JsonResponse
    {
        $request->validate([
            'timesteps' => 'integer|min:1000|max:1000000'
        ]);

        try {
            $response = Http::timeout(60)->post("{$this->backendUrl}/retrain/{$symbol}", [
                'timesteps' => $request->timesteps ?? 50000
            ]);
            
            if ($response->successful()) {
                $data = $response->json();
                Log::info('Agent retraining started', $data);
                
                return response()->json([
                    'success' => true,
                    'message' => 'Agent retraining started',
                    'data' => $data
                ]);
            }
            
            Log::error('Failed to start retraining', ['response' => $response->body()]);
            return response()->json([
                'success' => false,
                'message' => 'Failed to start retraining',
                'error' => $response->body()
            ], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error starting retraining', ['symbol' => $symbol, 'error' => $e->getMessage()]);
            return response()->json([
                'success' => false,
                'message' => 'Error communicating with trading bot',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get system logs
     */
    public function logs(): JsonResponse
    {
        try {
            $response = Http::timeout(10)->get("{$this->backendUrl}/logs");
            
            if ($response->successful()) {
                $data = $response->json();
                
                return response()->json([
                    'success' => true,
                    'data' => $data
                ]);
            }
            
            return response()->json([
                'success' => false,
                'message' => 'Failed to get logs',
                'error' => $response->body()
            ], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error getting logs', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => false,
                'message' => 'Error communicating with trading bot',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Health check for the backend
     */
    public function health(): JsonResponse
    {
        try {
            $response = Http::timeout(5)->get("{$this->backendUrl}/health");
            
            if ($response->successful()) {
                $data = $response->json();
                
                return response()->json([
                    'success' => true,
                    'data' => $data,
                    'backend_connected' => true
                ]);
            }
            
            return response()->json([
                'success' => false,
                'message' => 'Backend unhealthy',
                'backend_connected' => false,
                'error' => $response->body()
            ], $response->status());
            
        } catch (Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Cannot connect to backend',
                'backend_connected' => false,
                'error' => $e->getMessage()
            ], 500);
        }
    }

    // Advanced Training System Methods

    /**
     * Search for stocks
     */
    public function searchStocks(Request $request): JsonResponse
    {
        try {
            $query = $request->get('query');
            $response = Http::timeout(30)->get("{$this->backendUrl}/training/search-stocks", [
                'query' => $query
            ]);
            
            if ($response->successful()) {
                return response()->json($response->json());
            }
            
            return response()->json(['error' => 'Failed to search stocks'], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error searching stocks', ['error' => $e->getMessage()]);
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    /**
     * Get stock information
     */
    public function stockInfo(Request $request, string $symbol): JsonResponse
    {
        try {
            $response = Http::timeout(30)->get("{$this->backendUrl}/training/stock-info/{$symbol}");
            
            if ($response->successful()) {
                return response()->json($response->json());
            }
            
            return response()->json(['error' => 'Failed to get stock info'], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error getting stock info', ['error' => $e->getMessage()]);
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    /**
     * Import historical data
     */
    public function importData(Request $request): JsonResponse
    {
        try {
            $response = Http::timeout(60)->post("{$this->backendUrl}/training/import-data", $request->all());
            
            if ($response->successful()) {
                return response()->json($response->json());
            }
            
            return response()->json(['error' => 'Failed to import data'], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error importing data', ['error' => $e->getMessage()]);
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    /**
     * Train advanced model
     */
    public function trainModel(Request $request): JsonResponse
    {
        try {
            $response = Http::timeout(30)->post("{$this->backendUrl}/training/train-model", $request->all());
            
            if ($response->successful()) {
                return response()->json($response->json());
            }
            
            return response()->json(['error' => 'Failed to train model'], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error training model', ['error' => $e->getMessage()]);
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    /**
     * Run simulation
     */
    public function simulation(Request $request): JsonResponse
    {
        try {
            $response = Http::timeout(60)->post("{$this->backendUrl}/training/simulation", $request->all());
            
            if ($response->successful()) {
                return response()->json($response->json());
            }
            
            return response()->json(['error' => 'Failed to run simulation'], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error running simulation', ['error' => $e->getMessage()]);
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    /**
     * Get training status
     */
    public function trainingStatus(Request $request): JsonResponse
    {
        try {
            $trainingId = $request->get('training_id');
            $response = Http::timeout(30)->get("{$this->backendUrl}/training/status", [
                'training_id' => $trainingId
            ]);
            
            if ($response->successful()) {
                return response()->json($response->json());
            }
            
            return response()->json(['error' => 'Failed to get training status'], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error getting training status', ['error' => $e->getMessage()]);
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    /**
     * Get available models
     */
    public function availableModels(Request $request): JsonResponse
    {
        try {
            $response = Http::timeout(30)->get("{$this->backendUrl}/training/models");
            
            if ($response->successful()) {
                return response()->json($response->json());
            }
            
            return response()->json(['error' => 'Failed to get models'], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error getting models', ['error' => $e->getMessage()]);
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    /**
     * Save/export a trained model
     */
    public function saveModel(Request $request): JsonResponse
    {
        $request->validate([
            'symbol' => 'required|string|max:10',
            'model_name' => 'sometimes|string|max:100',
            'description' => 'sometimes|string|max:255'
        ]);

        try {
            $response = Http::timeout(30)->post("{$this->backendUrl}/training/save-model", [
                'symbol' => $request->symbol,
                'model_name' => $request->model_name,
                'description' => $request->description ?? ''
            ]);
            
            if ($response->successful()) {
                return response()->json($response->json());
            }
            
            return response()->json(['error' => 'Failed to save model'], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error saving model', ['error' => $e->getMessage()]);
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    /**
     * Get list of saved models
     */
    public function getSavedModels(): JsonResponse
    {
        try {
            $response = Http::timeout(30)->get("{$this->backendUrl}/training/saved-models");
            
            if ($response->successful()) {
                return response()->json($response->json());
            }
            
            return response()->json(['error' => 'Failed to get saved models'], $response->status());
            
        } catch (Exception $e) {
            Log::error('Error getting saved models', ['error' => $e->getMessage()]);
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }
}