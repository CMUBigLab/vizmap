//
//  ViewController.swift
//  VizMapDemo
//
//  Created by Gierad Laput on 4/20/16.
//  Copyright © 2016 FIGLab. All rights reserved.
//

import UIKit
import AVFoundation

class ViewController: UIViewController, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
    
    let imagePicker = UIImagePickerController()
    var sampleImage : UIImage = UIImage()
    
    @IBOutlet var imageView: UIImageView!
    @IBOutlet var activityIndicator: UIActivityIndicatorView!
    @IBOutlet var statusText: UITextView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Grab Captured Session
        imagePicker.delegate = self
        sampleImage = UIImage(named:"sample.jpg")!
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    @IBAction func launchCamera(sender: UIButton) {
        imagePicker.allowsEditing = false
        imagePicker.sourceType = .Camera
        presentViewController(imagePicker, animated: true, completion: nil)
    }
    
    
    // MARK: - UIImagePickerControllerDelegate Methods
    func imagePickerController(picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [String : AnyObject]) {
        if let pickedImage = info[UIImagePickerControllerOriginalImage] as? UIImage {
            // Do something with Image
            /*
            pickedImage.resize(CGSizeMake(1686,2448), completionHandler: { [weak self](resizedImage, data) -> () in
                let image = resizedImage
                self?.imageView.contentMode = .ScaleAspectFit
                self?.imageView.image = image
                print("Photo dimensions: \(image.size.width), \(image.size.height)")
            });
             */
            
            imageView.contentMode = .ScaleAspectFit
            imageView.image = sampleImage
            //imageUploadRequest(sampleImage)
            self.statusText.text = "Photo dimensions: \(pickedImage.size.width), \(pickedImage.size.height)"

        }
        
        dismissViewControllerAnimated(true, completion: nil)
        
    }
    
    func exploreRequest(img: UIImage) {
        
    }
    
    
    func createMessageRequest(img: UIImage)
    {

        // New Endpoints
        /*
         curl http://hulop.qolt.cs.cmu.edu:5000/createMessage -F "map=cole-qolt" -F "user=1-shrink-0.75" -F "image=@/Users/cole/Desktop/test.jpg" -F "message=testing"
         
         {"y": 2.738004467063922, "x": -0.7169097806563904, "message": "testing", "z": 1.6316144325782747, "id": 2}
         
         curl http://hulop.qolt.cs.cmu.edu:5000/nearbyMessages -F "map=cole-qolt" -F "user=1-shrink-0.75" -F "image=@/Users/cole/Desktop/test.jpg"
         {"location": {"R": [[-4.554151430203731, -0.08702704631592698, -0.22964427468859822], [0.31518542161788116, 1.0717123943843165, -4.017395788115996], [0.23032585849168274, -3.8835742611655926, -1.4763317055616705]], "t": [-0.6804651650577891, 2.770635341301171, 1.6196015241721344]}, "nearby": [{"message": "testing", "direction": "2 o'clock"}, {"message": "testing", "direction": "2 o'clock"}]}
 
        */
        
        
        let request = NSMutableURLRequest(URL: NSURL(string: "http://hulop.qolt.cs.cmu.edu:5000/nearby")!);
        request.HTTPMethod = "POST";
        
        let param = [
            "map"   : "cole-qolt",
            "user"  : "1-shrink-0.75",
            "radius" : "100",
        ]
        
        let boundary = generateBoundaryString()
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        let imageData = UIImageJPEGRepresentation(img, 1)
        if(imageData==nil)  { return; }
        
        request.HTTPBody = createBodyWithParameters(param, filePathKey: "image", imageDataKey: imageData!, boundary: boundary)
        
        activityIndicator.hidden = false;
        activityIndicator.startAnimating();

        let task = NSURLSession.sharedSession().dataTaskWithRequest(request) {
            data, response, error in
            
            if error != nil {
                dispatch_async(dispatch_get_main_queue(),{
                    self.statusText.text = error!.localizedFailureReason
                    self.activityIndicator.stopAnimating()
                });
                return
            }
            
            // Response object:
            // print("******* response = \(response)")
            
            // Response string:
            // let responseString = NSString(data: data!, encoding: NSUTF8StringEncoding)
            // print("****** response data = \(responseString!)")
            
            dispatch_async(dispatch_get_main_queue(),{
                self.activityIndicator.stopAnimating()
                self.activityIndicator.hidden = true;
                var json:AnyObject
                do {
                    json = try NSJSONSerialization.JSONObjectWithData(data!, options: .AllowFragments)
                    if let items = json["nearby"] as? [[String: AnyObject]] {
                        var out: String = "Objects around you "
                        for item in items {
                            out += "," + String(item["direction"]!) + ", " + String(item["description"]!)
                        }
                        UIAccessibilityPostNotification(UIAccessibilityAnnouncementNotification, out)
                        self.statusText.text = out
                    } else {
                        self.statusText.text = String(json["description"])
                    }
                } catch {
                    self.statusText.text = "error serializing JSON: \(error)"
                }
            });
        }
        task.resume()
    }
    
    
    func createBodyWithParameters(parameters: [String: String]?, filePathKey: String?, imageDataKey: NSData, boundary: String) -> NSData {
        let body = NSMutableData();
        if parameters != nil {
            for (key, value) in parameters! {
                body.appendString("--\(boundary)\r\n")
                body.appendString("Content-Disposition: form-data; name=\"\(key)\"\r\n\r\n")
                body.appendString("\(value)\r\n")
            }
        }
        
        let filename = "device_upload.jpg"
        let mimetype = "image/jpg"
        
        body.appendString("--\(boundary)\r\n")
        body.appendString("Content-Disposition: form-data; name=\"\(filePathKey!)\"; filename=\"\(filename)\"\r\n")
        body.appendString("Content-Type: \(mimetype)\r\n\r\n")
        body.appendData(imageDataKey)
        body.appendString("\r\n")
        body.appendString("--\(boundary)--\r\n")
        return body
    }
    
    func generateBoundaryString() -> String {
        return "Boundary-\(NSUUID().UUIDString)"
    }
    
}
