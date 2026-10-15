package dev.pyxpo.modules.sharing

import android.content.ClipData
import android.content.Intent
import android.net.Uri
import android.webkit.MimeTypeMap
import dev.pyxpo.moduleapi.PxModule
import dev.pyxpo.moduleapi.PxModuleContext
import dev.pyxpo.moduleapi.PxReply
import org.json.JSONArray
import java.io.File

/** System share sheet. Files must live in the app's cache or files folder. Like react-native, Android always reports sharedAction. */
class ShareModule : PxModule() {
    override val name = "Share"

    override fun call(ctx: PxModuleContext, method: String, args: JSONArray, reply: PxReply) {
        if (method != "share") { reply(null, "unknown native call Share.$method"); return }
        val paths = args.optJSONArray(0) ?: JSONArray()
        val message = args.optString(1, "")
        val app = ctx.activity
        val uris = ArrayList<Uri>()
        val mimes = HashSet<String>()
        try {
            for (i in 0 until paths.length()) {
                val raw = paths.optString(i)
                val f = File(if (raw.startsWith("file://")) Uri.parse(raw).path ?: raw else raw)
                if (!f.isFile) { reply(null, "file not found: ${f.name}"); return }
                uris.add(PxShareFileProvider.uriFor(app, f))
                mimes.add(MimeTypeMap.getSingleton().getMimeTypeFromExtension(f.extension.lowercase()) ?: "application/octet-stream")
            }
        } catch (e: IllegalArgumentException) {
            reply(null, e.message ?: "file can not be shared"); return
        }
        val intent = Intent(if (uris.size > 1) Intent.ACTION_SEND_MULTIPLE else Intent.ACTION_SEND)
        intent.type = when {
            uris.isEmpty() -> "text/plain"
            mimes.size == 1 -> mimes.first()
            mimes.all { it.startsWith("image/") } -> "image/*"
            else -> "*/*"
        }
        if (message.isNotEmpty()) intent.putExtra(Intent.EXTRA_TEXT, message)
        if (uris.size == 1) intent.putExtra(Intent.EXTRA_STREAM, uris[0])
        else if (uris.size > 1) intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
        if (uris.isNotEmpty()) {
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.clipData = ClipData.newRawUri("", uris[0]).also { c -> for (u in uris.drop(1)) c.addItem(ClipData.Item(u)) }
        }
        try {
            app.startActivity(Intent.createChooser(intent, null))
            reply(mapOf("action" to "sharedAction"), null)
        } catch (e: Throwable) {
            reply(null, e.message ?: e.toString())
        }
    }
}
