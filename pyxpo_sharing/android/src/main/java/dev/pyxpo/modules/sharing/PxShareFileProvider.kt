package dev.pyxpo.modules.sharing

import android.content.ContentProvider
import android.content.ContentValues
import android.content.Context
import android.database.Cursor
import android.database.MatrixCursor
import android.net.Uri
import android.os.ParcelFileDescriptor
import android.provider.OpenableColumns
import android.webkit.MimeTypeMap
import java.io.File
import java.io.FileNotFoundException

/**
 * Read-only provider for the share sheet. Serves only files inside the app's cache and files folders,
 * addressed as content://<applicationId>.pyxpo.share/<absolute path>. Plain ContentProvider, so no AndroidX is needed.
 */
class PxShareFileProvider : ContentProvider() {
    override fun onCreate() = true

    private fun resolve(uri: Uri): File {
        val ctx = context ?: throw FileNotFoundException("no context")
        val f = File("/" + uri.pathSegments.joinToString("/")).canonicalFile
        if (!allowedRoots(ctx).any { f.path.startsWith(it.path + File.separator) } || !f.isFile) throw FileNotFoundException(uri.toString())
        return f
    }

    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor {
        if (mode != "r") throw FileNotFoundException("read-only")
        return ParcelFileDescriptor.open(resolve(uri), ParcelFileDescriptor.MODE_READ_ONLY)
    }

    override fun getType(uri: Uri): String? = try {
        MimeTypeMap.getSingleton().getMimeTypeFromExtension(resolve(uri).extension.lowercase()) ?: "application/octet-stream"
    } catch (e: FileNotFoundException) { null }

    override fun query(uri: Uri, projection: Array<String>?, selection: String?, selectionArgs: Array<String>?, sortOrder: String?): Cursor {
        val f = resolve(uri)
        val cols = projection ?: arrayOf(OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE)
        val cur = MatrixCursor(cols)
        cur.addRow(Array<Any?>(cols.size) { i -> when (cols[i]) { OpenableColumns.DISPLAY_NAME -> f.name; OpenableColumns.SIZE -> f.length(); else -> null } })
        return cur
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? = throw UnsupportedOperationException("read-only")
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<String>?): Int = throw UnsupportedOperationException("read-only")
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<String>?): Int = throw UnsupportedOperationException("read-only")

    companion object {
        private fun allowedRoots(ctx: Context) = listOf(ctx.cacheDir.canonicalFile, ctx.filesDir.canonicalFile)

        fun uriFor(ctx: Context, file: File): Uri {
            val f = file.canonicalFile
            if (!allowedRoots(ctx).any { f.path.startsWith(it.path + File.separator) }) {
                throw IllegalArgumentException("only files in the app's cache or files folder can be shared")
            }
            return Uri.Builder().scheme("content").authority(ctx.packageName + ".pyxpo.share").path(f.path).build()
        }
    }
}
