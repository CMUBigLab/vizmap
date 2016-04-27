//
//  LeaveMessageViewController.swift
//  VizMapMessages
//
//  Created by Gierad Laput on 4/27/16.
//  Copyright © 2016 FIGLab. All rights reserved.
//

import UIKit

class LeaveMessageViewController: UIViewController, UINavigationControllerDelegate, UIImagePickerControllerDelegate {

    @IBOutlet var imagePreview: UIImageView!
    @IBOutlet var imageStatus: UILabel!
    @IBOutlet var submitButton: UIButton!
    @IBOutlet var messageTextField: UITextField!
    @IBOutlet var activityIndicator: UIActivityIndicatorView!
    
    var imagePicker = UIImagePickerController()
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // Do any additional setup after loading the view.
        imagePicker.delegate = self
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    @IBAction func takePhoto(sender: UIButton) {
        imagePicker.sourceType = .Camera
        presentViewController(imagePicker, animated: true, completion: nil)
    }
    
    @IBAction func createVizMapMessageRequest(sender: AnyObject) {
        newMessageRequest(imagePreview.image!, msg: messageTextField.text!)
    }
    
    override func touchesBegan(touches: Set<UITouch>, withEvent event: UIEvent?) {
        messageTextField.resignFirstResponder()
        if imagePreview.image != nil {
            submitButton.enabled = true
        }
    }
    
    func imagePickerController(picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [String : AnyObject]) {
        if let pickedImage = info[UIImagePickerControllerOriginalImage] as? UIImage {
            // Do something with Image
            imagePreview.contentMode = .ScaleAspectFit
            imagePreview.image = pickedImage
            self.imageStatus.text = "Dimensions: \(pickedImage.size.width), \(pickedImage.size.height)"
        
            if (!messageTextField.text!.isEmpty) {
                submitButton.enabled = true
            }
        }
        
        dismissViewControllerAnimated(true, completion: nil)
        
    }
    
    func newMessageRequest(img: UIImage, msg: String)
    {
        
        /*
        curl http://hulop.qolt.cs.cmu.edu:5000/createMessage -F "map=cole-qolt" -F "user=1-shrink-0.75" -F "image=@/Users/cole/Desktop/test.jpg" -F "message=testing"
        
        {"y": 2.738004467063922, "x": -0.7169097806563904, "message": "testing", "z": 1.6316144325782747, "id": 2}
        */
        
        let request = NSMutableURLRequest(URL: NSURL(string: "http://hulop.qolt.cs.cmu.edu:5000/createMessage")!);
        request.HTTPMethod = "POST";
        
        let param = [
            "map"   : "cole-qolt",
            "user"  : "1-shrink-0.75",
            "message" : msg,
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
                    self.imageStatus.text = error!.localizedFailureReason
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
                    if let response = json["message"] as? String {
                        self.imageStatus.text = "Messaged saved: \(response)"
                        // Return
                        self.navigationController?.popViewControllerAnimated(true)
                    } else {
                        self.imageStatus.text = "An error occured"
                    }
                } catch {
                    self.imageStatus.text = "error serializing JSON: \(error)"
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
