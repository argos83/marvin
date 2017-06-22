
if [ "$TRAVIS_PULL_REQUEST" = false ] ; then
    echo "Releasing new version of Marvin"
    git config --global user.name "semantic-release"
    git config --global user.email "semantic-release@travis"
    pip install python-semantic-release
    semantic-release publish
else
    echo "Branch: Skipping release"
fi
