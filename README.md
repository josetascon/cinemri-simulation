CineMR Simulation
-----------------

This is a patient-specific 2D Cine-MRI simulator capable to generate a simulated ground truth contour of the desired organs using pre-treatment images. The input images are a 4DCT scan and an 3D MR with organ contours. The video simulator has the following input parameters: video time, frames per second, breathing cycle time, breathing amplitude, and additive noise.

Desing
------

Figure [CineMR Simulator][./design/cinemr_simulation.png] illustrates the video simulation process. The process comprises two stages: breathing modeling and video synthesis. The breathing model is a pre-processing stage and uses full 3D information to consider out-of-plane motion in the 2D Cine-MRI. The video synthesis stage can be run several times changing the simulation parameters to create different variants and motion conditions. 

Dependencies
------------

Python:
* yaml
* numpy
* matplotlib
* pydicom
* skimage
* SimpleITK >= 2.0

External:
* ANTs [webpage](http://stnava.github.io/ANTs/)

---

Simulation
----------

To run a simulation you require a set of images. A sample image folder is provided in 'images/sample'. Create a cinemr with simulation using the command line as:

  python simulation.py -v images/patient/ model/patient/ out/ parameters.yaml
 

Citation
--------

To cite when using this toolbox, please reference, as appropriate:
@inproceedings{tascon2021cine,
  title={Cine-MRI simulation to evaluate tumor tracking},
  author={Tascón-Vidarte, José D. and Wahlstedt, Isak and Jomier, Julien and Erleben, Kenny and
  Vogelius, Ivan R. and Darkner, Sune},
  booktitle={International Workshop on Simulation and Synthesis in Medical Imaging},
  pages={1--10},
  year={2021},
  organization={Springer}
}


References
----------

Tascón-Vidarte J.D., Wahlstedt I., Jomier J., Erleben K., Vogelius I.R. and Darkner S. "Cine-MRI simulation to evaluate tumor tracking" International Workshop on Simulation and Synthesis in Medical Imaging. Springer, Cham, 2021.