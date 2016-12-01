using UnityEngine;
using System.Collections;
using Assets.Scripts.ResData;
using tnt_deploy;

public class Test : MonoBehaviour {
	void Start () {
        //GOODS_INFO_ARRAY对应的结构：GOODS_INFO
        var bytes = ResDataManager.Instance.ReadDataConfig("goods_info.bin");
        Debug.Log(GOODS_INFO_ARRAY.ItemsFieldNumber);
        GOODS_INFO_ARRAY arr = GOODS_INFO_ARRAY.ParseFrom(bytes);
        Debug.Log("Length: " + arr.ItemsCount);

        var oneTemp = arr.ItemsList[0];
        Debug.Log("Id: " + oneTemp.GoodsId + "  OnlineTime: " + oneTemp.OnlineTime.ToStringUtf8());

        var bytes2 = ResDataManager.Instance.ReadDataConfig("person_info.bin");
        PERSON_INFO_ARRAY arr2 = PERSON_INFO_ARRAY.ParseFrom(bytes2);
        Debug.Log("Length: " + arr2.ItemsCount);
        for (int i = 0; i < arr2.ItemsCount; i++)
        {
            PERSON_INFO personInfo = arr2.ItemsList[i];
            Debug.Log("Id: " + personInfo.Id + "  Name: " + personInfo.Name.ToStringUtf8());
        }
    }
}
