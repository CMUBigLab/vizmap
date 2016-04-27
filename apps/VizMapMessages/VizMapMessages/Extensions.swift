//
//  ImageResize.swift
//  VizMapDemo
//
//  Created by Gierad Laput on 4/20/16.
//  Copyright © 2016 FIGLab. All rights reserved.
//

import Foundation
import UIKit

extension UIImage {
    public func resize(size:CGSize, completionHandler:(resizedImage:UIImage, data:NSData)->()) {
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), { () -> Void in
            let newSize:CGSize = size
            let rect = CGRectMake(0, 0, newSize.width, newSize.height)
            UIGraphicsBeginImageContextWithOptions(newSize, false, 1.0)
            self.drawInRect(rect)
            let newImage = UIGraphicsGetImageFromCurrentImageContext()
            UIGraphicsEndImageContext()
            let imageData = UIImageJPEGRepresentation(newImage, 0.5)
            dispatch_async(dispatch_get_main_queue(), { () -> Void in
                completionHandler(resizedImage: newImage, data:imageData!)
            })
        })
    }
}

extension NSMutableData {
    func appendString(string: String) {
        let data = string.dataUsingEncoding(NSUTF8StringEncoding, allowLossyConversion: true)
        appendData(data!)
    }
    
}