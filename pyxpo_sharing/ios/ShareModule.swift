import UIKit

/// System share sheet (UIActivityViewController). Replies once the sheet closes.
final class ShareModule: PxModule {
    static let moduleName = "Share"

    required init() {}

    func call(_ ctx: PxModuleContext, _ method: String, _ args: [Any], _ reply: @escaping PxReply) {
        guard method == "share" else { reply(nil, "unknown native call Share.\(method)"); return }
        let paths = (args.first as? [Any])?.compactMap { $0 as? String } ?? []
        let message = (args.count > 1 ? args[1] as? String : nil) ?? ""
        var items: [Any] = []
        if !message.isEmpty { items.append(message) }
        for p in paths {
            let path = p.hasPrefix("file://") ? (URL(string: p)?.path ?? p) : p
            guard FileManager.default.fileExists(atPath: path) else { reply(nil, "file not found: \((path as NSString).lastPathComponent)"); return }
            items.append(URL(fileURLWithPath: path))
        }
        guard let top = ctx.presenter() else { reply(nil, "no view controller to present the share sheet"); return }
        let vc = UIActivityViewController(activityItems: items, applicationActivities: nil)
        vc.completionWithItemsHandler = { _, completed, _, err in
            if let err = err { reply(nil, err.localizedDescription); return }
            reply(["action": completed ? "sharedAction" : "dismissedAction"], nil)
        }
        if let pop = vc.popoverPresentationController {
            pop.sourceView = top.view
            pop.sourceRect = CGRect(x: top.view.bounds.midX, y: top.view.bounds.midY, width: 0, height: 0)
            pop.permittedArrowDirections = []
        }
        top.present(vc, animated: true)
    }
}
