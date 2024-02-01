from typing import Dict, Tuple
import sys
import os
import platform
import tempfile
import subprocess
from argparse import ArgumentParser, HelpFormatter

subprocess.call([ 'pip', 'install' , 'inquirer', '-q' ])

import inquirer

from facefusion import metadata, wording

TORCH : Dict[str, str] =\
{
	'default': 'default',
	'cpu': 'cpu'
}
ONNXRUNTIMES : Dict[str, Tuple[str, str]] =\
{
	'default': ('onnxruntime', '1.17.0')
}
if platform.system().lower() == 'linux' or platform.system().lower() == 'windows':
	TORCH['cuda-12.1'] = 'cu121'
	TORCH['cuda-11.8'] = 'cu118'
	ONNXRUNTIMES['cuda-12.1'] = ('onnxruntime-gpu', '1.17.0')
	ONNXRUNTIMES['cuda-11.8'] = ('onnxruntime-gpu', '1.17.0')
	ONNXRUNTIMES['openvino'] = ('onnxruntime-openvino', '1.16.0')
if platform.system().lower() == 'linux':
	TORCH['rocm-5.4.2'] = 'rocm5.4.2'
	TORCH['rocm-5.6'] = 'rocm5.6'
	ONNXRUNTIMES['rocm-5.4.2'] = ('onnxruntime-rocm', '1.16.3')
	ONNXRUNTIMES['rocm-5.6'] = ('onnxruntime-rocm', '1.16.3')
if platform.system().lower() == 'windows':
	ONNXRUNTIMES['directml'] = ('onnxruntime-directml', '1.17.0')


def cli() -> None:
	program = ArgumentParser(formatter_class = lambda prog: HelpFormatter(prog, max_help_position = 120))
	program.add_argument('--torch', help = wording.get('install_dependency_help').format(dependency = 'torch'), choices = TORCH.keys())
	program.add_argument('--onnxruntime', help = wording.get('install_dependency_help').format(dependency = 'onnxruntime'), choices = ONNXRUNTIMES.keys())
	program.add_argument('--skip-venv', help = wording.get('skip_venv_help'), action = 'store_true')
	program.add_argument('-v', '--version', version = metadata.get('name') + ' ' + metadata.get('version'), action = 'version')
	run(program)


def run(program : ArgumentParser) -> None:
	args = program.parse_args()
	python_id = 'cp' + str(sys.version_info.major) + str(sys.version_info.minor)

	if not args.skip_venv:
		os.environ['PIP_REQUIRE_VIRTUALENV'] = '1'
	if args.torch and args.onnxruntime:
		answers =\
		{
			'torch': args.torch,
			'onnxruntime': args.onnxruntime
		}
	else:
		answers = inquirer.prompt(
		[
			inquirer.List('torch', message = wording.get('install_dependency_help').format(dependency = 'torch'), choices = list(TORCH.keys())),
			inquirer.List('onnxruntime', message = wording.get('install_dependency_help').format(dependency = 'onnxruntime'), choices = list(ONNXRUNTIMES.keys()))
		])
	if answers:
		torch = answers['torch']
		torch_wheel = TORCH[torch]
		onnxruntime = answers['onnxruntime']
		onnxruntime_name, onnxruntime_version = ONNXRUNTIMES[onnxruntime]

		subprocess.call([ 'pip', 'uninstall', 'torch', '-y', '-q' ])
		if torch_wheel == 'default':
			subprocess.call([ 'pip', 'install', '-r', 'requirements.txt', '--force-reinstall' ])
		else:
			subprocess.call([ 'pip', 'install', '-r', 'requirements.txt', '--extra-index-url', 'https://download.pytorch.org/whl/' + torch_wheel, '--force-reinstall' ])
		if onnxruntime == 'rocm-5.4.2' or onnxruntime == 'rocm-5.6':
			if python_id in [ 'cp39', 'cp310', 'cp311' ]:
				rocm_version = onnxruntime.replace('-', '')
				rocm_version = rocm_version.replace('.', '')
				wheel_name = 'onnxruntime_training-' + onnxruntime_version + '+' + rocm_version + '-' + python_id + '-' + python_id + '-manylinux_2_17_x86_64.manylinux2014_x86_64.whl'
				wheel_path = os.path.join(tempfile.gettempdir(), wheel_name)
				wheel_url = 'https://download.onnxruntime.ai/' + wheel_name
				subprocess.call([ 'curl', '--silent', '--location', '--continue-at', '-', '--output', wheel_path, wheel_url ])
				subprocess.call([ 'pip', 'uninstall', wheel_path, '-y', '-q' ])
				subprocess.call([ 'pip', 'install', wheel_path, '--force-reinstall' ])
				os.remove(wheel_path)
		else:
			subprocess.call([ 'pip', 'uninstall', 'onnxruntime', onnxruntime_name, '-y', '-q' ])
			if onnxruntime == 'cuda-12.1':
				subprocess.call([ 'pip', 'install', onnxruntime_name + '==' + onnxruntime_version, '--extra-index-url', 'https://pkgs.dev.azure.com/onnxruntime/onnxruntime/_packaging/onnxruntime-cuda-12/pypi/simple', '--force-reinstall' ])
			else:
				subprocess.call([ 'pip', 'install', onnxruntime_name + '==' + onnxruntime_version, '--force-reinstall' ])
