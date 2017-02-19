import os
import pkg_resources


def get_package_details_from_filepath(filepath=None):
    if filepath is None:
        import traceback
        stack = traceback.extract_stack()
        calling_frame = stack[1]
        filepath = calling_frame[0]

    def in_same_location(pkg):
        return pkg.location in filepath

    packages = list(filter(in_same_location, pkg_resources.working_set))
    file_to_check = filepath.replace(packages[0].location, '')[1:]

    for pkg in packages:
        escaped_project_name = pkg.project_name.replace('-', '_')
        record_file = '{}/{}-{}.dist-info/RECORD'.format(pkg.location, escaped_project_name, pkg.version)
        if os.path.isfile(record_file):
            if file_to_check in open(record_file).read():
                return pkg
    raise Exception('Package not found!')


if __name__ == "__main__":
    print(get_package_details_from_filepath())
