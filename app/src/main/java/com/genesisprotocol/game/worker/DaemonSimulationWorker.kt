package com.genesisprotocol.game.worker

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters

class DaemonSimulationWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        return Result.success()
    }
}
