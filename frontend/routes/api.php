<?php

use App\Http\Controllers\TradingBotController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});

// Trading Bot API Routes - Read-only endpoints (no auth required)
Route::prefix('bot')->group(function () {
    Route::get('/status', [TradingBotController::class, 'status'])->name('bot.status');
    Route::get('/health', [TradingBotController::class, 'health'])->name('bot.health');
    Route::get('/logs', [TradingBotController::class, 'logs'])->name('bot.logs');
    Route::get('/evaluate/{symbol}', [TradingBotController::class, 'evaluate'])->name('bot.evaluate');
});

// Trading Bot API Routes - Write operations (auth required)
Route::middleware(['auth:sanctum,web'])->prefix('bot')->group(function () {
    Route::post('/start', [TradingBotController::class, 'start'])->name('bot.start');
    Route::post('/stop', [TradingBotController::class, 'stop'])->name('bot.stop');
    Route::post('/switch-mode', [TradingBotController::class, 'switchMode'])->name('bot.switch-mode');
    Route::post('/configure', [TradingBotController::class, 'configure'])->name('bot.configure');
    Route::post('/retrain/{symbol}', [TradingBotController::class, 'retrain'])->name('bot.retrain');
});

// Advanced Training API Routes - Read-only endpoints (no auth required)
Route::prefix('training')->group(function () {
    Route::get('/search-stocks', [TradingBotController::class, 'searchStocks'])->name('training.search-stocks');
    Route::get('/stock-info/{symbol}', [TradingBotController::class, 'stockInfo'])->name('training.stock-info');
    Route::get('/status', [TradingBotController::class, 'trainingStatus'])->name('training.status');
    Route::get('/models', [TradingBotController::class, 'availableModels'])->name('training.models');
});

// Advanced Training API Routes - Write operations (auth required)
Route::middleware(['auth:sanctum,web'])->prefix('training')->group(function () {
    Route::post('/import-data', [TradingBotController::class, 'importData'])->name('training.import-data');
    Route::post('/train-model', [TradingBotController::class, 'trainModel'])->name('training.train-model');
    Route::post('/simulation', [TradingBotController::class, 'simulation'])->name('training.simulation');
    Route::post('/save-model', [TradingBotController::class, 'saveModel'])->name('training.save-model');
    Route::get('/saved-models', [TradingBotController::class, 'getSavedModels'])->name('training.saved-models');
}); 