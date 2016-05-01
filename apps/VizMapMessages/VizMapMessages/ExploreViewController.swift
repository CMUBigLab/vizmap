//
//  ExploreViewController.swift
//  VizMapMessages
//
//  Created by Gierad Laput on 4/27/16.
//  Copyright © 2016 FIGLab. All rights reserved.
//

import UIKit

class ExploreViewController: UIViewController, UINavigationControllerDelegate, UIImagePickerControllerDelegate  {

    @IBOutlet var activityIndicator: UIActivityIndicatorView!
    @IBOutlet var previewImage: UIImageView!
    @IBOutlet var statusMessage: UITextView!
    
    var imagePicker = UIImagePickerController()
    var sampleImage: UIImage = UIImage()
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        imagePicker.delegate = self
        sampleImage = UIImage(named:"sample.jpg")!
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    @IBAction func takePhoto(sender: AnyObject) {
        imagePicker.sourceType = .Camera
        presentViewController(imagePicker, animated: true, completion: nil)
    }
    
    func imagePickerController(picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [String : AnyObject]) {
        if let pickedImage = info[UIImagePickerControllerOriginalImage] as? UIImage {
            // Do something with Image
            previewImage.contentMode = .ScaleAspectFit
            previewImage.image = pickedImage
            newExploreMessagesRequest(pickedImage)
            self.statusMessage.text = "Dimensions: \(pickedImage.size.width), \(pickedImage.size.height)"
        }
        
        dismissViewControllerAnimated(true, completion: nil)
        
    }
    
    func newExploreMessagesRequest(img: UIImage)
    {
        /*
         curl http://hulop.qolt.cs.cmu.edu:5000/nearbyMessages -F "map=cole-qolt" -F "user=1-shrink-0.75" -F "image=@/Users/cole/Desktop/test.jpg"
         {"location": {"R": [[-4.554151430203731, -0.08702704631592698, -0.22964427468859822], [0.31518542161788116, 1.0717123943843165, -4.017395788115996], [0.23032585849168274, -3.8835742611655926, -1.4763317055616705]], "t": [-0.6804651650577891, 2.770635341301171, 1.6196015241721344]}, "nearby": [{"message": "testing", "direction": "2 o'clock"}, {"message": "testing", "direction": "2 o'clock"}]}
         
         */
 
        let request = NSMutableURLRequest(URL: NSURL(string: "http://hulop.qolt.cs.cmu.edu:5000/nearbyMessages")!);
        request.HTTPMethod = "POST";
        
        let param = [
            "map"   : "cole-qolt",
            "user"  : "1-shrink-0.75",
            "radius" : "5",
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
                    self.statusMessage.text = error!.localizedFailureReason
                    self.activityIndicator.stopAnimating()
                });
                return
            }
            
            dispatch_async(dispatch_get_main_queue(),{
                self.activityIndicator.stopAnimating()
                self.activityIndicator.hidden = true;
                
                var json:AnyObject
                do {
                    json = try NSJSONSerialization.JSONObjectWithData(data!, options: .AllowFragments)
                    print(json)
                    if let items = json["nearby"] as? [[String: AnyObject]] {
                        var out: String = "Nearby messages "
                        for item in items {
                            out += "," + String(item["direction"]!) + ", " + String(item["message"]!)
                        }
                        UIAccessibilityPostNotification(UIAccessibilityAnnouncementNotification, out)
                        self.statusMessage.text = out
                    } else {
                        self.statusMessage.text = "An error occured"
                    }
                } catch {
                    self.statusMessage.text = "error serializing JSON: \(error)"
                }
            });
        }
        task.resume()
    }

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepareForSegue(segue: UIStoryboardSegue, sender: AnyObject?) {
        // Get the new view controller using segue.destinationViewController.
        // Pass the selected object to the new view controller.
    }
    */

}
