package com.genesisprotocol.game.audio

import android.content.Context
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer

class GenesisAudioDirector(context: Context) {
    private val player = ExoPlayer.Builder(context).build()

    fun playAtmosphere(uri: String) {
        player.setMediaItem(MediaItem.fromUri(uri))
        player.repeatMode = ExoPlayer.REPEAT_MODE_ALL
        player.prepare()
        player.playWhenReady = true
    }

    fun stop() {
        player.stop()
    }

    fun release() {
        player.release()
    }
}
