using UnityEngine;
using System.Collections;
using UFramework;
using Assets.Scripts.ResData;

public class Test : MonoBehaviour {
	void Start () {
        //GOODS_INFO_ARRAY对应的结构：GOODS_INFO
        var bytes = ResDataManager.Instance.ReadDataConfig("goods_info.bin");
        Debug.Log(GOODS_INFO_ARRAY.ItemsFieldNumber);
        //GOODS_INFO_ARRAY arr = GOODS_INFO_ARRAY.Parser.ParseFrom(bytes);
        //Debug.Log("Length: " + arr.Items.Count);

        var bytes2 = ResDataManager.Instance.ReadDataConfig("person_info.bin");
        PERSON_INFO_ARRAY arr2 = PERSON_INFO_ARRAY.Parser.ParseFrom(bytes2);
        Debug.Log("Length: " + arr2.Items.Count);
        for (int i = 0; i < arr2.Items.Count; i++)
        {
            PERSON_INFO personInfo = arr2.Items[i];
            Debug.Log("Name: " + personInfo.Name /*+ "   " + personInfo.*/);
        }
    }
}
