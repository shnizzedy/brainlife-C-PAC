import nibabel as nib
import numpy as np
import scipy.io
import h5py
import numpy as np
import os
import nibabel as nib
from scipy import stats
import scipy.io
from CPAC.QPP.QPPv0418 import qpp_wf,BSTT,TBLD2WL,regressqpp
import time




def qppv(img,mask,wl,cth,n_itr_th,mx_itr,pfs,nsubj,nrn):

    if img.endswith('.mat'):

        D_file = scipy.io.loadmat(img)

        for keys in D_file:
            D = D_file['D']
        D = np.array(D)

    else:
        ##This is the function to import the img into an array object
        ##D_file is now an array object
        ##nib is nibabel package
        D_file = nib.load(img)
        D_img = D_file.dataobj
        D_img=np.array(D_img)
        if len(D_img.shape) == 3:
        ##shape of D_img is (61,73,61,7)
            raise Exception("Warning!! The input image you have provided is not of the right shape for further analysis!"\
                  "please provide the right data")


        D_img = D_img.reshape(D_img.shape[0]*D_img.shape[1],D_img.shape[2],D_img.shape[3])

        ##D_img is now (4453,61,7)
        D = [[None]*nrn]*nsubj
        #each element of D[i] should be of size (D_img.shape[0],D_img.shape[1]*D_img.shape[2])
        ##initializing D, which is a list of lists
        for i in range(nsubj):
            for j in range(nrn):
                D[i][j] = D_img[:,:,i+j*nsubj]

        ##copy D_img to D


    if  mask.endswith('.nii'):
        data1 = nib.load(mask)
        msk_img = np.array(data1.dataobj)
        #import msk

        #reshape for masks
        msk_shape = msk_img.shape[:-1]
        m_voxels = np.prod(msk_img.shape[:-1])
        msk = msk_img.reshape(m_voxels,msk_img.shape[-1])

    else:  #we have to remove this, only keeping this for testing
        msk_file = h5py.File(mask)
        msk_img = msk_file['M']
        msk_img = np.array(msk_img)
        msk_shape = msk_img.shape[:-1]
        m_voxels = np.prod(msk_img.shape[:-1])
        msk = msk_img.reshape(m_voxels,msk_img.shape[-1])


    nx = D[0][0].shape[0]
    nt = D[0][0].shape[1]
    nd = nsubj*nrn
    nrp=nd
    nt_new = nt * nd
    B = np.zeros((nx,nt_new))
    id =1
    for isbj in range(nsubj):
        for irn in range(nrn):
                B[:,(id-1)*nt:id*nt] = (stats.zscore(D[isbj][irn],axis=1))
                id += 1

    B=np.around(B, decimals=4)
    msk = np.zeros((nx,1))
    msk[(np.sum(abs(B)) > 0)] = 1
    A = np.isnan(B)
    B[A] = 0

    with open('b.txt','w') as f:
        for line in B:
            f.write("%s\n" %line)


    start_time = time.time()
    #generate qpp
    time_course, ftp, itp, iter = qpp_wf(B, msk, nd, wl, nrp, cth, n_itr_th, mx_itr, pfs)
    #choose best template
    C_1,FTP1,Met1 = BSTT(time_course,ftp,nd,B,pfs)
    #regress QPP
    T =TBLD2WL(B,wl,FTP1,pfs)
    Br, C1r=regressqpp(B, nd, T, C_1,pfs)
    print("-----%s seconds ----"%(time.time() - start_time))

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("img", type=str)
    parser.add_argument("mask",type=str)
    parser.add_argument("wl",type=int)
    parser.add_argument("cth",nargs='+',type=float)
    parser.add_argument("n_itr_th",type=int)
    parser.add_argument("mx_itr",type=int)
    parser.add_argument("pfs",type=str)
    parser.add_argument("nsubj",type=int)
    parser.add_argument("nrn",type=int)
    args = parser.parse_args()

    qppv(args.img,args.mask,args.wl,args.cth,args.n_itr_th,args.mx_itr,args.pfs,args.nsubj,args.nrn)



