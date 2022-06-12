# monocle
---
A command-line tool written in Python for automatically cropping images.

<table class="is-fullwidth">
</thead>
<tbody>
</tbody>
	<tr>
		<td>
			<center>
			<img src="./.github_readme/nightingale_closeup.jpg" width="96"><br />
			Original Image
			</center>
		</td>
		<td>
			<center>
			<img src="./.github_readme/nightingale_closeup_x_option.jpg" width="96"><br />
			Chunks Colored In
			</center>
		</td>
		<td>
			<center>
			<img src="./.github_readme/nightingale_closeup_y_option.jpg" width="96"><br />
			Background Detection in Chunks
			</center>
		</td>
		<td>
			<center>
			<img src="./.github_readme/nightingale_closeup_cropped.jpg" width="96"><br />
			Cropped Image
			</center>
		</td>
	</tr>
	<tr>
		<td>
			`sample/novel/small_2.jpg`
		</td>
		<td>
			`python3 interface.py -x -o 350 825 1950 3100 sample/novel/small_2.jpg`
		</td>
		<td>
			`python3 interface.py -y -o 350 825 1950 3100 sample/novel/small_2.jpg`
		</td>
		<td>
			`python3 interface.py -o 350 825 1950 3100 sample/novel/small_2.jpg`
		</td>
</table>

## Functionality in a Nutshell
It crops the image to include only the subject in the image(the main object of attention);