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
    
    override func viewDidLoad() {
        super.viewDidLoad()
        self.title = "VizMap Messages"
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


    @IBAction func showExploreView(sender: UIButton) {
        
    }
    
    @IBAction func showLeaveMessageView(sender: UIButton) {
        //let storyboard = UIStoryboard(name: "Main", bundle: nil)
        //let vc = storyboard.instantiateViewControllerWithIdentifier("LeaveMessageViewController")
        //self.navigationController?.pushViewController(vc, animated: true)
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
        
       
    }

    
}
