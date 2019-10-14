"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy as np
import os, sys, platform

dependencies = []
# include all header files, to recognize changes
for dirpath, dirnames, filenames in os.walk("singleeyefitter"):
    for filename in [f for f in filenames if f.endswith(".h")]:
        dependencies.append(os.path.join(dirpath, filename))

root_dir_include_path = "."
detector_2d_include_path = "pupil_detectors/detector_2d"
shared_cpp_include_path = "shared_cpp/include"
singleeyefitter_include_path = "singleeyefitter/"


if platform.system() == "Windows":
    libs = []
    library_dirs = []
    lib_spec = [
        [np.get_include(), ""],
        [
            "C:\\work\\opencv\\build\\include",
            "C:\\work\\opencv\\build\\x64\\vc14\\lib\\opencv_world345.lib",
        ],
        ["C:\\work\\ceres-windows\\Eigen", ""],
        [
            "C:\\work\\ceres-windows\\ceres-solver\\include",
            "C:\\work\\ceres-windows\\x64\\Release\\ceres_static.lib",
        ],
        [
            "C:\\work\\ceres-windows\\glog\\src\\windows",
            "C:\\work\\ceres-windows\\x64\\Release\\libglog_static.lib",
        ],
        ["C:\\work\\ceres-windows", ""],
    ]

    include_dirs = [spec[0] for spec in lib_spec]
    include_dirs.append(root_dir_include_path)
    include_dirs.append(detector_2d_include_path)
    include_dirs.append(shared_cpp_include_path)
    include_dirs.append(singleeyefitter_include_path)
    xtra_obj2d = [spec[1] for spec in lib_spec]

else:
    # opencv3 - highgui module has been split into parts: imgcodecs, videoio, and highgui itself
    opencv_libraries = [
        "opencv_core",
        "opencv_highgui",
        "opencv_videoio",
        "opencv_imgcodecs",
        "opencv_imgproc",
        "opencv_video",
    ]

    # explicit lib and include dirs for homebrew installed opencv
    opencv_library_dirs = [
        "/usr/local/opt/opencv/lib",  # old opencv brew (v3)
        "/usr/local/opt/opencv@3/lib",  # new opencv@3 brew
        "/usr/local/lib",  # new opencv brew (v4)
    ]
    opencv_include_dirs = [
        "/usr/local/opt/opencv/include",  # old opencv brew (v3)
        "/usr/local/opt/opencv@3/include",  # new opencv@3 brew
        "/usr/local/include/opencv4",  # new opencv brew (v4)
    ]
    opencv_core_found = any(
        os.path.isfile(path + "/libopencv_core.so") for path in opencv_library_dirs
    )
    if not opencv_core_found:
        ros_dists = ["kinetic", "jade", "indigo"]
        for ros_dist in ros_dists:
            ros_candidate_path = "/opt/ros/" + ros_dist + "/lib"
            if os.path.isfile(ros_candidate_path + "/libopencv_core3.so"):
                opencv_library_dirs = [ros_candidate_path]
                opencv_include_dirs = [
                    "/opt/ros/" + ros_dist + "/include/opencv-3.1.0-dev"
                ]
                opencv_libraries = [lib + "3" for lib in opencv_libraries]
                break
    include_dirs = [
        np.get_include(),
        "/usr/local/include/eigen3",
        "/usr/include/eigen3",
        root_dir_include_path,
        detector_2d_include_path,
        shared_cpp_include_path,
        singleeyefitter_include_path,
    ] + opencv_include_dirs
    libs = ["ceres"] + opencv_libraries
    xtra_obj2d = []
    library_dirs = opencv_library_dirs

extra_compile_args = ["-D_USE_MATH_DEFINES", "-std=c++11", "-w", "-O2"]
if platform.system() == "Windows":
    # TODO: This is a quick and dirty fix for:
    # https://github.com/pupil-labs/pupil/issues/1331 We should investigate this more
    # and fix it correctly at some point.
    extra_compile_args += ["-D_ENABLE_EXTENDED_ALIGNED_STORAGE"]

extensions = [
    Extension(
        name="pupil_detectors.detector_base",
        sources=["pupil_detectors/detector_base.pyx"],
        language="c++",
    ),
    Extension(
        name="pupil_detectors.detector_2d.detector_2d",
        sources=[
            "pupil_detectors/detector_2d/detector_2d.pyx",
            "singleeyefitter/ImageProcessing/cvx.cpp",
            "singleeyefitter/utils.cpp",
            "singleeyefitter/detectorUtils.cpp",
        ],
        include_dirs=include_dirs,
        libraries=libs,
        library_dirs=library_dirs,
        extra_link_args=[],  # '-WL,-R/usr/local/lib'
        extra_compile_args=extra_compile_args,
        extra_objects=xtra_obj2d,
        depends=dependencies,
        language="c++",
    ),
    # Extension(
    #     name="pupil_detectors.detector_3d.detector_3d",
    #     sources=[
    #         "pupil_detectors/detector_3d/detector_3d.pyx",
    #         "singleeyefitter/ImageProcessing/cvx.cpp",
    #         "singleeyefitter/utils.cpp",
    #         "singleeyefitter/detectorUtils.cpp",
    #         "singleeyefitter/EyeModelFitter.cpp",
    #         "singleeyefitter/EyeModel.cpp",
    #     ],
    #     include_dirs=include_dirs,
    #     libraries=libs,
    #     library_dirs=library_dirs,
    #     extra_link_args=[],  # '-WL,-R/usr/local/lib'
    #     extra_compile_args=extra_compile_args,
    #     extra_objects=xtra_obj2d,
    #     depends=dependencies,
    #     language="c++",
    # ),
]

if __name__ == "__main__":
    setup(
        name="pupil_detectors",
        version="0.2",
        packages=["pupil_detectors"],
        url="https://github.com/pupil-labs/pupil-detectors",
        author="Pupil Labs",
        author_email="info@pupil-labs.com",
        license="GNU",
        ext_modules=cythonize(extensions, quiet=True, nthreads=8),
    )
