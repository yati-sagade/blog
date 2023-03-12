---
date: 2014-11-02

layout: post

title: Setting up OpenCV for Android without an IDE

---

Getting OpenCV running on Android without an IDE like Android Studion or
Eclipse is actually very simple. It is just underdocumented. So here it is.

Installing the SDKs
---------------------

If you haven't already done so, install the [Android SDK][1] and make sure the
'/tools' directory in the SDK directory is on the system path. Now download the
[OpenCV Android SDK][2] and unpack it in your workspace.

    $ unzip OpenCV-2.4.x-android-sdk.zip

Another tool you need to install in order to be able to build from the command
line is `ant`.

The `android` tool
-----------------------

The `android` script, which can be found in `<android-sdk-dir>/tools` directory,
is the primary tool we'll use to manage our Android project from the command
line. You can read more about it [here][3].

To use this and other SDK tools, it is convenient to add the
`<android-sdk-dir>/tools` directory on the system path.


Creating a new Android app project
------------------------------------

To create a new project using the `android` tool, do
    
    $ android create project --target 1 --name myproject\
      --activity MainActivity --path myproject --package com.myproject


Note here the value taken by the `--target` option. It specifies the API level
to build your project against. To see a list of available targets on your
system, do
    
    $ android list

And pick a target number. You can always install new target runtime APIs and
other supporting libraries using the SDK manager, which you can invoke like so:
    
    $ android

Just to verify that everything is working fine, connect an Android device to
your dev machine, and compile and install the project, like so:
    
    $ ant debug && adb install -r bin/myproject-debug.apk

The app (called "MainActivity") should now have been installed on your device.

Setting up the OpenCV for Android library project
-------------------------------------------------

To properly initialize the OpenCV for Android SDK to use your target runtimes,
go to the SDK library, which in my case at this point is 
`../OpenCV-2.4.x-android-sdk/sdk/java` and do
    
    $ android update lib-project --target 1 --path .


Referencing the OpenCV for Android library
------------------------------------------

Returning to our workspace, we should now have an Android app stub in
`./myproject`. Now we need to make this project reference the OpenCV Android
SDK. Do this like so
    
    $ cd myproject
    $ android update project --path . --library ../OpenCV-2.4.x-android-sdk/sdk/java


Requesting the permission to use the hardware camera
-----------------------------------------------------

Change your `AndroidManifest.xml` to look like this:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
        package="com.myproject"
        android:versionCode="1"
        android:versionName="1.0">
    <application android:label="@string/app_name" android:icon="@drawable/ic_launcher">
        <activity android:name="MainActivity"
                    android:label="@string/app_name"
                    android:theme="@android:style/Theme.NoTitleBar.Fullscreen"
                    android:screenOrientation="landscape"
                    android:configChanges="keyboardHidden|orientation">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

    <uses-permission android:name="android.permission.CAMERA" />
    <uses-feature android:name="android.hardware.camera"
                    android:required="false"/>
    <uses-feature android:name="android.hardware.camera.autofocus"
                    android:required="false"/>
    <uses-feature android:name="android.hardware.camera.front"
                    android:required="false"/>
    <uses-feature android:name="android.hardware.camera.front.autofocus"
                    android:required="false"/>

</manifest>
```

The only change here is the addition of the permission declarations near the
end and two attributes in the `<activity>` tag that are generally used in
most camera applications.

Adding the camera view to the layout
------------------------------------

Change your `res/layout/main.xml` to look like this:

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    xmlns:opencv="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent" >

    <org.opencv.android.JavaCameraView
        android:layout_width="fill_parent"
        android:layout_height="fill_parent"
        android:visibility="gone"
        android:id="@+id/cameraview"
        opencv:show_fps="true"
        opencv:camera_id="any" />

</LinearLayout>
```

This uses a `SurfaceView` provided by the OpenCV SDK, called the
`JavaCameraView`. This class handles the drawing of the preview frames and
delivering them to our application for realtime processing.

Camera initialization
----------------------

OpenCV is a native library and has Java wrappers for Android. Because of this,
we need to explicitly load the library before we attempt to use it. Note that
failing to do so will cause your app to crash with an `UnsatisfiedLinkError`.

Here's the code for `src/com/myproject/MainActivity.java`. We'll walk through
it in a while.

```java
package com.myproject;

import org.opencv.android.*;
import org.opencv.core.*;
import org.opencv.imgproc.*;
import org.opencv.android.CameraBridgeViewBase.CvCameraViewListener2;
import org.opencv.android.CameraBridgeViewBase.CvCameraViewFrame;

import android.app.Activity;
import android.os.Bundle;
import android.view.SurfaceView;
import android.util.Log;


public class MainActivity extends Activity implements CvCameraViewListener2
{
    private CameraBridgeViewBase cameraView = null;
    private static final String tag = "myproject";
    
    // This is called when OpenCV is loaded or when there is an error
    // while loading OpenCV.
    private BaseLoaderCallback opencvLoaderCallback = new BaseLoaderCallback(this) {
        @Override
        public void onManagerConnected(int status) {
            switch (status) {
            case LoaderCallbackInterface.SUCCESS:
            {
                Log.d(tag, "Loaded OpenCV successfully");
                // Init camera and start preview.
                cameraView.enableView();
            } break;

            default:
                super.onManagerConnected(status);
            }
        }
    };

    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        cameraView = (CameraBridgeViewBase) findViewById(R.id.cameraview);
        cameraView.setVisibility(SurfaceView.VISIBLE);
        cameraView.setCvCameraViewListener(this);

    }

    @Override
    public void onResume() {
        super.onResume();

        // Load the OpenCV library asynchronously. The callback object
        // opencvLoaderCallback will be notified when this is complete.
        OpenCVLoader.initAsync(OpenCVLoader.OPENCV_VERSION_2_4_3, this, opencvLoaderCallback); 
    }

    @Override
    public void onPause() {
        super.onPause();
        
        // Release the camera.
        if (cameraView != null) {
            cameraView.disableView();
            cameraView = null;
        }
    }

    // Begin implementation of CvCameraViewListener2
    
    // This method is called for every preview frame. It should return a
    // Mat object representing the frame to be showed to the user.
    @Override
    public Mat onCameraFrame(CvCameraViewFrame frame) {
        return frame.gray(); 
    }

    @Override
    public void onCameraViewStarted(int width, int height) {

    }

    @Override
    public void onCameraViewStopped() {

    }

    // End implementation of CvCameraViewListener2
}
```


Compile and install this app like so
    
    $ ant debug && adb install -r bin/myproject-debug.apk

When you open the app first time, you may see a dialog that asks your
permission to install the OpenCV manager app on the phone. Install that app
and run MainActivity. You should now see a grayscale preview with an FPS count.


Code walkthrough
-----------------

Most of the code is really easy to understand. Here's the typical flow of
events when the app is started.

- `onCreate()` is called, which sets up the layout and initializes local
  variables.
- `onResume()` is called, which requests for an async loading of OpenCV for
  Android. This is accomplished via the `OpenCVLoader.initAsync()` call, which,
  among other arguments, takes a `BaseLoaderCallback` object which is notified
  when loading is complete. In our implementation of the callback, we just
  enable the preview.
- `onPause()` is called whenever the app is backgrounded by the user. We use
  this to release the camera. This is important because if we do not release
  the camera properly, no other app, including our own app can subsequently
  open the camera.
- `onCameraFrame()`, a part of the `CvCameraViewListener2` interface, is
  called on _every preview frame_. It is the job of this method to process
  each frame and return a frame as a `Mat` object which will then be displayed
  to the user as preview. We are just returning a grayscale version of each
  frame now, which is available via `CvCameraViewFrame.gray()`. There is
  also `CvCameraView.rgba()`, which returns a `Mat` object in the RGBA
  format. For more information, refer to the [Javadocs for OpenCV for Android][4].


Canny edge detection
---------------------

As a last demonstration of how processed frames are drawn on the preview, we'll
modify `onCameraFrame()` to detect edges in every frame.

```java
@Override
public Mat onCameraFrame(CvCameraViewFrame frame) {
    Mat gray = frame.gray(); 
    Imgproc.Canny(gray, gray, 80, 100, 3, true);
    return gray;
}
```

Here, the `org.opencv.imgproc.Imgproc.Canny()` routine is used to detect
edges and the resultant image with just edge information is returned, which
is then drawn as preview.


Final words
-----------
Some people can't imagine writing Android apps without an IDE. I can't imagine
struggling with bloat just to try something out quickly. There are some
excellent plugins for both vim and emacs that make writing Java bearable
without the bloated, slow and bug ridden IDEs.


[1]: https://developer.android.com/sdk/index.html?hl=i
[2]: http://sourceforge.net/projects/opencvlibrary/files/opencv-android/
[3]: http://developer.android.com/tools/projects/projects-cmdline.html
[4]: http://docs.opencv.org/java/overview-summary.html

