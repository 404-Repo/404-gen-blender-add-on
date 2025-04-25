# 404—GEN BLENDER ADD-ON
[![Discord](https://img.shields.io/discord/1065924238550237194?logo=discord&logoColor=%23FFFFFF&logoSize=auto&label=Discord&labelColor=%235865F2)](https://discord.gg/404gen)
[![Create Release](https://github.com/404-Repo/three-gen-blender-plugin/actions/workflows/create-release.yml/badge.svg)](https://github.com/404-Repo/three-gen-blender-plugin/actions/workflows/create-release.yml)

*404—GEN leverages decentralized AI to transform your words into detailed 3D models, bringing your ideas to life in just one minute*  
[Project Repo](https://github.com/404-Repo/three-gen-subnet) | [Website](https://404.xyz/) | [X](https://x.com/404gen_)

## About
- This repository is specifically for the Blender add-on and does not include the 404—GEN Discord bot or web front-end.  
- With this add-on, users can:
  - Enter text prompts to generate **3D Gaussian Splats**
  - Import .ply files
  - Convert .ply to **mesh**

## Installation
### Software requirements
Blender 4.2+

### Instructions
1. Download the latest release from this repo [or Gumroad](https://404gen.gumroad.com/l/blender) and **_do not unzip_**
   
  <img width="480" alt="release" src="https://github.com/user-attachments/assets/e91a8530-43bb-49bd-bffe-a2540f038c25">

  <img width="480" alt="download" src="https://github.com/user-attachments/assets/0373bedd-578a-4b46-903f-9e88a4918d57">


2. In Blender, Edit ➡️ Preferences ➡️ Add-ons ➡️ Install ➡️ Select the add-on ZIP file
   
  <img width="480" alt="install" src="https://github.com/user-attachments/assets/cf4710b1-4660-4c77-ae1c-be21ac23e515">


> [!NOTE]
> If you have a previous version of this add-on enabled, you will need to uninstall it and restart Blender before installing the new version. You may also need to restart Blender after installing the new version.

3. Check the box to enable the add-on, then click Install Dependencies and accept the anonymous usage data notice (you may opt out after reading the notice).
   
  <img width="480" alt="addon-enable" src="https://github.com/user-attachments/assets/92145edb-012e-4279-b0e6-bbc401af346f">

> [!NOTE]
> Windows 10 users may have to open Blender as admin before installing Dependencies

> [!IMPORTANT]
> Do not change the URL or API key


🌟 404 tab should now appear in the sidebar 🌟

  <img width="480" alt="404-UI" src="https://github.com/user-attachments/assets/72ac61fb-d0ae-4cef-9434-5ae760760c52">


## Usage
### Generating
Type your prompt and click Generate. Each generation should take **approximately 1 minute**.

> [!NOTE]
>- For best results, describe a single object/element for each generation, rather than an entire scene or room at once.
>- To view the material in object or edit mode, open the Shading Menu (shortcut z) and select Material Preview (shortcut 2).

### Settings and Mesh Generation
After the splat is generated or imported, the **Splat Display Settings** and **Mesh Conversion** dropdown menus will appear.

> [!CAUTION]
> Applying the geometry nodes modifier will convert to a very high poly mesh that will greatly decrease in quality if simplified. For higher visual quality and lower poly count, use the Generate Mesh button.

  <img width="320" alt="sliders_0 9 0" src="https://github.com/user-attachments/assets/c79ab713-bfb6-41a3-b52a-b22f4d7c11ca">

#### Splat Display Settings
- **Opacity Threshold:** Gaussian Splats are often generated with fully or partially transparent ellipsoids. Ellipsoids with an opacity below the set threshold will be hidden.
- **Display Percentage:** Sets the percentage of the entire Gaussian Splat to display.
- **Min Detail Size:** Determines the amount of detail to be included in the generated mesh. A lower value will generate a higher level of detail.
- **Simplify:** Simplifies the generated mesh. A higher value will lead to a smoother, more decimated mesh.
- **Angle Limit:** Adjusts the UV map's angle limit. The default is recommended unless the mesh generates with black/missing spots in the texture, in which case the limit should be lowered.
- **Texture Size:** The size of the texture in pixels.
- **Generate Mesh:** This will generate a mesh of the selected Gaussian Splat based on the above values. The mesh will overlap and have the same name as the Gaussian Splat, but they are two sepate objects in the collection.

  <img width="1440" alt="mesh_0 9 0" src="https://github.com/user-attachments/assets/7993a277-b5b4-4217-8432-fd634d11efcb">

> [!NOTE]
> For questions or help troubleshooting, join our [Discord server](https://discord.gg/404gen).
