<?php

use App\Http\Controllers\ProfileController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\TradingBotController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;

Route::get('/', function () {
    return Inertia::render('Welcome', [
        'canLogin' => Route::has('login'),
        'canRegister' => Route::has('register'),
        'laravelVersion' => Application::VERSION,
        'phpVersion' => PHP_VERSION,
    ]);
});

// Trading Bot Dashboard Routes
Route::middleware(['auth', 'verified'])->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');
    Route::get('/advanced', [DashboardController::class, 'index'])->name('advanced');
    Route::get('/configuration', [DashboardController::class, 'configuration'])->name('configuration');
    Route::get('/analytics', [DashboardController::class, 'analytics'])->name('analytics');
    Route::get('/logs', [DashboardController::class, 'logs'])->name('logs');
});

// Trading Bot API Routes
Route::middleware(['auth'])->prefix('api/bot')->group(function () {
    Route::post('/start', [TradingBotController::class, 'start'])->name('bot.start');
    Route::post('/stop', [TradingBotController::class, 'stop'])->name('bot.stop');
    Route::get('/status', [TradingBotController::class, 'status'])->name('bot.status');
    Route::post('/switch-mode', [TradingBotController::class, 'switchMode'])->name('bot.switch-mode');
    Route::post('/configure', [TradingBotController::class, 'configure'])->name('bot.configure');
    Route::get('/evaluate/{symbol}', [TradingBotController::class, 'evaluate'])->name('bot.evaluate');
    Route::post('/retrain/{symbol}', [TradingBotController::class, 'retrain'])->name('bot.retrain');
    Route::get('/logs', [TradingBotController::class, 'logs'])->name('bot.logs');
    Route::get('/health', [TradingBotController::class, 'health'])->name('bot.health');
});

// Profile Routes
Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';
