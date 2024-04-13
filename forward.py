from gaussian_splatting import *


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ply", help="the ply path")
    args = parser.parse_args()

    if args.ply:
        # "/home/liu/workspace/gaussian-splatting/output/fb15ba66-e/point_cloud/iteration_30000/point_cloud.ply
        ply_fn = args.ply
        print("Try to load %s ..." % ply_fn)
        gs = load_ply(ply_fn)
    else:
        print("not fly file.")
        exit(0)

    # Camera info
    tcw = np.array([1.03796196, 0.42017467, 4.67804612])
    Rcw = np.array([[0.89699204,  0.06525223,  0.43720409],
                    [-0.04508268,  0.99739184, -0.05636552],
                    [-0.43974177,  0.03084909,  0.89759429]]).T

    W = int(979)  # 1957  # 979
    H = int(546)  # 1091  # 546
    focal_x = 1163.2547280302354/2.
    focal_y = 1156.280404988286/2.

    K = np.array([[focal_x, 0, W/2.],
                  [0, focal_y, H/2.],
                  [0, 0, 1.]])

    Tcw = np.eye(4)
    Tcw[0:3, 0:3] = Rcw
    Tcw[0:3, 3] = tcw
    cam_center = np.linalg.inv(Tcw)[:3, 3]

    pw = gs['pos']
    # pw = np.vstack((pw.T, np.ones(pw.shape[0]))).T

    # step1. Transform the location to camera frame.
    pc = (Rcw @ pw.T).T + tcw

    # step2. Calcuate the 3d Gaussian.
    cov3d = compute_cov_3d(gs['scale'], gs['rot'])

    # step3. Project the 3D Gaussian to 2d image as a 2d Gaussian.
    cov2d = compute_cov_2d(pc, focal_x, focal_y, cov3d, Rcw)

    # step4. get color info
    ray_dir = pw[:, :3] - cam_center
    ray_dir /= np.linalg.norm(ray_dir, axis=1)[:, np.newaxis]
    color = sh2color(gs['sh'], ray_dir)

    # step5. Blend the 2d Gaussian to image
    image = blend(color, gs['alpha'], pc, K, cov2d, H, W)

    plt.imshow(image)

    plt.show()
