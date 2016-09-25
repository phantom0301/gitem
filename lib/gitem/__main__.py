#!/usr/bin/env python

from __future__ import print_function

import argparse

from gitem import api
from gitem import analytics


def leftpad_print(s, leftpad_length=0):
    print(" " * leftpad_length + s)


def organization(ghapi, *args, **kwargs):
    organization = kwargs['organization']
    verbose = kwargs['verbose']

    organization_info = analytics.get_organization_information(
        ghapi,
        organization
    )
    organization_repositories = analytics.get_organization_repositories(
        ghapi,
        organization
    )

    for human_readable_name, api_info in organization_info.items():
        leftpad_print(
            "{}: {}".format(human_readable_name, api_info),
            leftpad_length=0
        )

    leftpad_print("Repositories:", leftpad_length=0)

    def repository_popularity(repository):
        return (
            int(repository['Watchers']) +
            int(repository['Stars']) +
            int(repository['Forks'])
        )

    repositories = sorted(
        organization_repositories,
        key=repository_popularity,
        reverse=True
    )
    repository_count = len(organization_repositories) if verbose else 10
    repositories = repositories[:repository_count]

    for repository in repositories:
        for human_readable_name, api_info in repository.items():
            leftpad_print(
                "{}: {}".format(human_readable_name, api_info),
                leftpad_length=2
            )

        leftpad_print("Contributors:", leftpad_length=2)

        repository_name = repository['Repository Name']
        repository_contributors = analytics.get_repository_contributors(
            ghapi,
            organization,
            repository_name
        )
        contributor_count = len(repository_contributors) if verbose else 10

        for contributor in repository_contributors[:contributor_count]:
            for human_readable_name, api_info in contributor.items():
                leftpad_print(
                    "{}: {}".format(human_readable_name, api_info),
                    leftpad_length=4
                )

        leftpad_print("", leftpad_length=0)


def repository(ghapi, *args, **kwargs):
    pass


def user(ghapi, *args, **kwargs):
    pass


def parse_args():
    p = argparse.ArgumentParser(description='''
        A Github organization reconnaissance tool.
        ''', formatter_class=argparse.RawTextHelpFormatter)

    p.add_argument(
        '-o',
        '--oauth2-token',
        action='store',
        help='OAuth2 token for authentcation'
    )
    p.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='verbose output'
    )

    subparsers = p.add_subparsers(dest='command')

    organization = subparsers.add_parser('organization')
    organization.add_argument(
        'organization',
        action='store',
        help='Github organization name'
    )

    repository = subparsers.add_parser('repository')
    repository.add_argument(
        'repository',
        action='store',
        help='Github repository name'
    )

    user = subparsers.add_parser('user')
    user.add_argument(
        'user',
        action='store',
        help='Github user name'
    )

    args = p.parse_args()

    return args


def main():
    args = parse_args()

    dispatch = {
        "organization": organization,
        "repository": repository,
        "user": user,
    }

    ghapi = api.Api(args.oauth2_token)

    try:
        dispatch[args.command](ghapi, **vars(args))
    except api.ApiCallException as e:
        if e.rate_limiting:
            leftpad_print(
                "Your API requests are being rate-limited. " +
                "Please include an OAuth2 token and read the following:",
                leftpad_length=0
            )
            leftpad_print(e.rate_limiting_url, leftpad_length=0)
        else:
            # Re-raise original exception
            raise

if __name__ == "__main__":
    main()
