from github import Github
import json
import argparse
import pandas as pd
from get_bundle_id import get_single_bundle_id
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", help="Github token")
    args = parser.parse_args()
    token = args.token

    with open("apps.json", "r") as f:
        data = json.load(f)

    if os.path.exists("bundleId.csv"):
        df = pd.read_csv("bundleId.csv")
    else:
        df = pd.DataFrame(columns=["name", "bundleId"])

    # clear apps
    data["apps"] = []

    g = Github(token)
    repo = g.get_repo("swaggyP36000/TrollStore-IPAs")
    releases = repo.get_releases()

    for release in releases:
        print(release.title)

        for asset in release.get_assets():
            if (asset.name[-3:] != "ipa"):
                continue
            name = asset.name[:-4]
            date = asset.created_at.strftime("%Y-%m-%d")
            try:
                app_name, version = name.split("-", 1)
            except:
                app_name = name
                version = "1.0"

            if app_name in df.name.values:
                bundle_id = str(df[df.name == app_name].bundleId.values[0])
            else:
                bundle_id = get_single_bundle_id(asset.browser_download_url)
                df = pd.concat([df, pd.DataFrame(
                    {"name": [app_name], "bundleId": [bundle_id]})], ignore_index=True)

            data["apps"].append(
                {
                    "name": app_name,
                    "bundleIdentifier": bundle_id,
                    "version": version,
                    "versionDate": date,
                    "size": asset.size,
                    "downloadURL": asset.browser_download_url,
                    "developerName": "",
                    "localizedDescription": "",
                    "iconURL": f"https://raw.githubusercontent.com/swaggyP36000/TrollStore-IPAs/main/icons/{bundle_id}.png"
                }
            )

    df.to_csv("bundleId.csv", index=False)

    with open('apps.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
