package com.genesisprotocol.game

import android.os.Bundle
import android.view.SurfaceHolder
import android.view.SurfaceView
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.genesisprotocol.game.ui.GenesisHud

class MainActivity : ComponentActivity() {
    private val engine = NativeGenesisEngine()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        engine.initialize()
        setContent {
            MaterialTheme {
                Surface(color = Color(0xFF171A1C)) {
                    GenesisGame(engine)
                }
            }
        }
    }

    override fun onDestroy() {
        engine.shutdown()
        super.onDestroy()
    }
}

@Composable
private fun GenesisGame(engine: NativeGenesisEngine) {
    val status = remember { mutableStateOf(engine.statusLine()) }
    LaunchedEffect(Unit) {
        status.value = engine.statusLine()
    }
    Box(modifier = Modifier.fillMaxSize().background(Color(0xFF171A1C))) {
        VulkanSurface(engine)
        GenesisHud(status = status.value, modifier = Modifier.align(Alignment.TopStart).padding(16.dp))
        Text(
            text = "Genesis Protocol Vulkan Surface",
            color = Color(0xFFE7DFC9),
            modifier = Modifier.align(Alignment.BottomEnd).padding(16.dp)
        )
    }
}

@Composable
private fun VulkanSurface(engine: NativeGenesisEngine) {
    val context = LocalContext.current
    AndroidView(
        factory = {
            SurfaceView(context).apply {
                holder.addCallback(object : SurfaceHolder.Callback {
                    override fun surfaceCreated(holder: SurfaceHolder) = engine.attachSurface(holder.surface)
                    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) = engine.resize(width, height)
                    override fun surfaceDestroyed(holder: SurfaceHolder) = engine.detachSurface()
                })
            }
        },
        modifier = Modifier.fillMaxSize()
    )
    DisposableEffect(Unit) {
        onDispose { engine.detachSurface() }
    }
}
