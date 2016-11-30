using System;
using System.IO;
using UnityEngine;
using Google.Protobuf;
namespace Assets.Scripts.ResData
{
    class ResDataManager
    {
        private static ResDataManager sInstance;
        public static ResDataManager Instance
        {
            get
            {
                if(null== sInstance)
                {
                    sInstance =new ResDataManager();
                }
                return sInstance;
            }
        }
        public byte[] ReadDataConfig(string FileName)
        {
            FileStream fs = GetDataFileStream(FileName);
            if(null!= fs)
            {
                byte[] bytes =new byte[(int)fs.Length];
                fs.Read(bytes, 0, (int)fs.Length);
                fs.Close();
                return bytes;
            }
            return null;
        }

        private FileStream GetDataFileStream(string fileName)
        {
            string filePath = GetDataConfigPath(fileName);
            if(File.Exists(filePath))
            {
                FileStream fs =new FileStream(filePath, FileMode.Open);
                return fs;
            }
            else
            {
                Debug.Log("不存在文件 ： " + fileName);
            }
            return null;
        }

        private string GetDataConfigPath(string fileName)
        {
            return Application.streamingAssetsPath +"/DataConfig/"+ fileName;
        }
    }
}
