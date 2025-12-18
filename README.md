# 404—GEN BLENDER ADD-ON
[![Discord](https://img.shields.io/discord/1065924238550237194?logo=discord&logoColor=%23FFFFFF&logoSize=auto&label=Discord&labelColor=%235865F2)](https://discord.gg/404gen)
[![Create Release](https://github.com/404-Repo/404-gen-blender-add-on/actions/workflows/create-release.yml/badge.svg)](https://github.com/404-Repo/404-gen-blender-add-on/actions/workflows/create-release.yml)



*404—GEN leverages decentralized AI to transform your words into detailed 3D models, bringing your ideas to life in just one minute*  
[Project Repo](https://github.com/404-Repo/404-gen-subnet) | [Website](https://404.xyz/) | [X](https://x.com/404gen_)

## About
- This repository is specifically for the Blender Add-on and does not include the 404—GEN Discord bot or web front-end.  
- With this add-on, users can:
  - Enter Text Prompts to generate **3D Gaussian Splats**.
  - Enter 2D Image Prompts to genrate **3D Gaussian Splats**.
  - Import .ply files
  - Convert .ply to **mesh**

## Installation
### Software requirements
Blender 4.5+

### Instructions
1. Download the latest release from this repo [or Gumroad](https://404gen.gumroad.com/l/blender) and **_do not unzip_**
   
<img width="1265" height="660" alt="Blender 2" src="https://github.com/user-attachments/assets/036eb813-1d99-4cd7-89a0-f1baabe2b9c5" />



2. In Blender, Edit ➡️ Preferences ➡️ Add-ons ➡️ Install ➡️ Select the add-on ZIP file

<img width="659" height="448" alt="image" src="https://github.com/user-attachments/assets/2776e8d3-692f-48a2-9f2c-f01b7af89e5e" />

> [!NOTE]
> If you have a previous version of this add-on enabled, you will need to uninstall it and restart Blender before installing the new version. You may also need to restart Blender after installing the new version.

3. Check the box to enable the add-on, then click Install Dependencies and accept the anonymous usage data notice (you may opt out after reading the notice).
   
<img width="655" height="444" alt="image" src="https://github.com/user-attachments/assets/f310764a-18c1-4ad7-a3d8-eec154cfee63" />

> [!NOTE]
> Windows 10 users may have to open Blender as admin before installing Dependencies

> [!IMPORTANT]
> Do not change the URL or API key


🌟 404 tab should now appear in the sidebar 🌟

<img width="410" height="310" alt="image" src="https://github.com/user-attachments/assets/e893cb64-9523-4eaf-ad03-6ca6edfda973" />

## Usage
### Generating Using Text Prompt.
Type your prompt into the Text Prompt Field and click Generate. Each generation should take **approximately 1 minute**.

<img width="410" height="310" alt="image" src="https://github.com/user-attachments/assets/4bcf195a-1cbd-4221-bdc1-b6d5db7bc52b" />

> [!NOTE]
>- For best results, describe a single object/element for each generation, rather than an entire scene or room at once.
>- To view the material in object or edit mode, open the Shading Menu (shortcut z) and select Material Preview (shortcut 2).

### Generating Using 2D Image Prompt.
Add your 2D Image Prompt by clicking the Open Image file icon. Navigate to the 2D prompt you wish to use and click Generate. 

<img width="475" height="472" alt="image" src="https://github.com/user-attachments/assets/4c0aede8-a32d-40f4-96a6-228f601e2a64" />

> [!NOTE]
>- For best results upload an high quality image of the object you wish to generate on a white background.
>- Maximum Image size is 1024x1024.

### Settings and Mesh Generation
After the splat is generated or imported, the **Splat Display Settings** and **Mesh Conversion** dropdown menus will appear.

> [!CAUTION]
> Applying the geometry nodes modifier will convert to a very high poly mesh that will greatly decrease in quality if simplified. For higher visual quality and lower poly count, use the Generate Mesh button.

<img width="399" height="743" alt="image" src="https://github.com/user-attachments/assets/d754558e-73f9-4c7c-89bd-4f93acfa1e67" />


#### Splat Display Settings
- **Opacity Threshold:** Gaussian Splats are often generated with fully or partially transparent ellipsoids. Ellipsoids with an opacity below the set threshold will be hidden.
- **Display Percentage:** Sets the percentage of the entire Gaussian Splat to display.
- **Min Detail Size:** Determines the amount of detail to be included in the generated mesh. A lower value will generate a higher level of detail.
- **Simplify:** Simplifies the generated mesh. A higher value will lead to a smoother, more decimated mesh.
- **Angle Limit:** Adjusts the UV map's angle limit. The default is recommended unless the mesh generates with black/missing spots in the texture, in which case the limit should be lowered.
- **Texture Size:** The size of the texture in pixels.
- **Generate Mesh:** This will generate a mesh of the selected Gaussian Splat based on the above values. The mesh will overlap and have the same name as the Gaussian Splat, but they are two sepate objects in the collection.

<img width="1536" height="842" alt="image" src="https://github.com/user-attachments/assets/45add281-0426-435e-a04b-3e6c4e5077ce" />

> [!NOTE]
> For questions or help troubleshooting, join our [Discord server](https://discord.gg/404gen).
