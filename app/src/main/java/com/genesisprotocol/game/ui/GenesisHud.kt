package com.genesisprotocol.game.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun GenesisHud(status: String, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .background(Color(0xCC171A1C), RoundedCornerShape(12.dp))
            .padding(16.dp)
    ) {
        Text("GENESIS PROTOCOL", color = Color(0xFFE7DFC9), fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(8.dp))
        Row {
            Meter(label = "Health", value = 0.86f, color = Color(0xFFB65A3C))
            Spacer(Modifier.width(12.dp))
            Meter(label = "Hashrate", value = 0.62f, color = Color(0xFF3D7F7A))
        }
        Spacer(Modifier.height(8.dp))
        Text(status, color = Color(0xFFD6B15E))
    }
}

@Composable
private fun Meter(label: String, value: Float, color: Color) {
    Column(modifier = Modifier.width(160.dp)) {
        Text(label, color = Color(0xFFE7DFC9))
        LinearProgressIndicator(progress = { value }, color = color, trackColor = Color(0xFF6E6A61))
    }
}
