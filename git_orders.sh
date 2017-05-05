#测试git是否能使用
git

# 初始配置git账号, 告诉git你的名字和你的邮箱。
# 注意global，global表示你的所有git仓库都会使用这个配置。
# TODO 如何使用一个git配置不同的账号。 比如有的代码提交到github.有的代码提交到公司git上面。
# 当然也可以对某个仓库指定不同的用户名和email。 TODO 尝试一下。
git config --global user.name "Your name"
git config --global user.email "email@example.com"

# 将某文件夹初始化为可提交git仓库的文件夹。进入此文件夹之后。
git init

# 将代码添加到仓库
git add xxx

# 将代码提交到仓库
git commit -m "the reason"

# 注意添加到仓库和提交到仓库的微妙区别。
# 其实add只是将代码提交到暂存区。提交到暂存区之后。情况就有些不一样了。 commit是将代码从暂存区提交到仓库。
# 你要清楚git为什么要做这个流程。
# 存放于暂存区的文件只是一个中间状态。 
# commit之后才算是提交到了库之中。

# 查看git库的状态
git status  # 可以简写为git st

# 查看某个文件当前状态和库里面改文件的状态的区别
git diff xxx

# 查看提交的日志
git log

# 查看简洁版的git日志
git log --pretty=oneline

# head 表示当前版本 一般是git log里面的最新的一个。上个版本是HEAD^ 再上个版本是HEAD^^
# 回退到上一个版本 
git reset --hard HEAD^


# git log只是记录了一部分的命令， 如果你有回退的版本号找不到的话，可以用这个命令去找。不过一定要记得commit的内容 查看所有的命令历史
git reflog


# 撤销修改。如果修改没有放到暂存区，那么修改就丢弃掉。如果修改已经放到暂存区了。那么checkout 不会丢弃这次修改。
# 如果想撤销掉已经放到暂存区的修改。 就只能使用git reset 命令了。
git checkout -- xxx

# 撤销掉已经放在暂存区的修改
git reset HEAD xxx
git checkout -- xxx

# 从本地的版本库之中删除掉某一个文件
git rm xxx
git commit -m "rm file xxx"

# 一不小心从本地删除掉一个文件，从库里面把文件恢复回来。
git checkout -- xxx

# 创建SSH key
# ssh-keygen -f test   -C "test key" -f之后是文件名. -C 之后是备注。
# ssh-keygen -t rsa -C "youremail@example.com" -t rsa 代表生成秘钥文件
# ssh-keygen -t [rsa|dsa]，将会生成密钥文件和私钥文件 id_rsa,id_rsa.pub或id_dsa,id_dsa.pub
# id_rsa.pub是公钥，可以放心的告诉别人。
ssh-keygen -t rsa -C "youremail@example.com"

# 把已有的本地仓库和远程仓库关联。然后把本地的内容推送到github仓库。
git remote add origin git@github.com:HongtsingWang/learngit.git

# 将本地的内容推送到远程仓库上面
# push 代表把本地仓库的内容推送到远程仓库。
# -u 是第一次向仓库里面提交内容的时候用的，以后就不会再用到了。
# git 这样就把本地的master分支和远程仓库的master分支关联起来了。
git push -u origin master
# 以后再次提交的时候，就可以省略掉-u命令了。
git push origin master

# TODO origin是什么意思？

# 从远程克隆一个仓库到本地
git clone xxx

# 创建一个新的分支
git checkout -b dev

# 查看现在在哪一个分支上面
git branch

# 将dev分支的工作成果合并到master分支上面
git merge dev

# 删除分支
git branch -d dev

# git 的一般流程是创建一个分支，在该分支上面工作。工作完成之后合并该分支。 最后删除该分支。

# 如果提交的时候发现了冲突，那么必须解决了冲突之后再提交。

# 查看分支合并图
git graph

# 禁用fast forward
git merge --no-ff -m "merge with no off" dev

# --no-ff参数就可以用普通模式合并
# TODO no-ff 和 fast forward 的关系并没有搞太懂

# 把当前工作储藏起来。等以后恢复现场继续工作
git stash

# 查看stash list
git stash list

# 恢复内容
git stash pop
# 或者
git stash apply

# 以上二者的区别在于是否要把stash 之中的内容全都删掉

# 如果直接删掉分支，而该分支的内容并没有合并的话，就会提示丢失掉修改。 只能强行删除
git branch -D xxx

# 远程仓库的默认名称就是origin
git remote

# 查看更详细的信息
git remote -v

# 要把本地master分支上面的内容推送到远程仓库里面就用
git push origin master

# 要是提交dev分支上面的内容呢
git push origin dev

# 给当前打上一个标签
git tag <name>

# 查看所有的标签
git tag

# 显示标签对应的信息
git show xxx

# 删除标签
git tag -d v1.0

# 推送标签到远程
git push origin v1.0

# 一次性推送所有的标签
git push origin --tags

# 如果希望你对克隆的库的修改能被原库接收。可以发起一个pull request.

# 让git显示颜色
git config --global color.ui true

# 配置别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
# 撤销暂存区的修改。将暂存区的修改放回工作区。
git config --global alias.unstage 'reset HEAD'

# 显示最后一次提交的信息
git config --global alias.last 'log -1'


