from itertools import combinations
import os
import sys
import javalang
from javalang.ast import Node
from anytree import AnyNode, RenderTree,PreOrderIter
import time
import pickle
import multiprocessing as mp
import pandas as pd
import math
# AST的预处理，文章没有具体提及，后续添加
nodetypedict = {
    'MethodDeclaration': 0,
    'Modifier': 1,
    'FormalParameter': 2,
    'ReferenceType': 3,
    'BasicType': 4,
    'LocalVariableDeclaration': 5,
    'VariableDeclarator': 6,
    'MemberReference': 7,
    'ArraySelector': 8,
    'Literal': 9,
    'BinaryOperation': 10,
    'TernaryExpression': 11,
    'IfStatement': 12,
    'BlockStatement': 13,
    'StatementExpression': 14,
    'Assignment': 15,
    'MethodInvocation': 16,
    'Cast': 17,
    'ForStatement': 18,
    'ForControl': 19,
    'VariableDeclaration': 20,
    'TryStatement': 21,
    'ClassCreator': 22,
    'CatchClause': 23,
    'CatchClauseParameter': 24,
    'ThrowStatement': 25,
    'WhileStatement': 26,
    'ArrayInitializer': 27,
    'ReturnStatement': 28,
    'Annotation': 29,
    'SwitchStatement': 30,
    'SwitchStatementCase': 31,
    'ArrayCreator': 32,
    'This': 33,
    'ConstructorDeclaration': 34,
    'TypeArgument': 35,
    'EnhancedForControl': 36,
    'SuperMethodInvocation': 37,
    'SynchronizedStatement': 38,
    'DoStatement': 39,
    'InnerClassCreator': 40,
    'ExplicitConstructorInvocation': 41,
    'BreakStatement': 42,
    'ClassReference': 43,
    'SuperConstructorInvocation': 44,
    'ElementValuePair': 45,
    'AssertStatement': 46,
    'ElementArrayValue': 47,
    'TypeParameter': 48,
    'FieldDeclaration': 49,
    'SuperMemberReference': 50,
    'ContinueStatement': 51,
    'ClassDeclaration': 52,
    'TryResource': 53,
    'MethodReference': 54,
    'LambdaExpression': 55,
    'InferredFormalParameter': 56
}


# 得到AST需要的数据，递归各节点遍历出一棵树 tree
def get_token(node):
    token = ''
    # print(isinstance(node, Node))
    # print(type(node))
    if isinstance(node, str):
        token = node
    elif isinstance(node, set):
        token = 'Modifier'
    elif isinstance(node, Node):
        token = node.__class__.__name__
    # print(node.__class__.__name__,str(node))
    # print(node.__class__.__name__, node)
    return token


def get_child(root):
    # print(root)
    if isinstance(root, Node):
        children = root.children
    elif isinstance(root, set):
        children = list(root)
    else:
        children = []

    def expand(nested_list):
        for item in nested_list:
            if isinstance(item, list):
                for sub_item in expand(item):
                    # print(sub_item)
                    yield sub_item
            elif item:
                # print(item)
                yield item

    return list(expand(children))


def createtree(root, node, nodelist, parent=None):
    id = len(nodelist)
    # print(id)
    token, children = get_token(node), get_child(node)
    if id == 0:
        root.token = token
    else:
        newnode = AnyNode(id=id, token=token, parent=parent)
    nodelist.append(node)
    for child in children:
        if id == 0:
            createtree(root, child, nodelist, parent=root)
        else:
            createtree(root, child, nodelist, parent=newnode)

def traversal(node,typedict):  # 递归遍历所有节点

    if node.children:
        for child in node.children:
            traversal(child,typedict)
    else:  # 遍历至叶子节点，往上依次输出父节点。
        try:
            node.token = typedict[node.token]
        except KeyError:
            if node.token not in nodetypedict:
                node.token = 'String'
        while node.parent:
            node = node.parent

# 代码数据预处理
def Buildast(programfile):
    # programfile = open(r"test.java", encoding='utf-8')
    # print(os.path.join(rt,file))
    programtext = programfile.read()
    # programtext=programtext.replace('\r','')
    programtokens = javalang.tokenizer.tokenize(programtext)
    # print("programtokens",list(programtokens))
    parser = javalang.parse.Parser(programtokens)
    programast = parser.parse_member_declaration()
    # print(programast)
    tree = programast
    nodelist = []
    newtree = AnyNode(id = 0,token=None)


   
    tokens = list(javalang.tokenizer.tokenize(programfile.read()))
    # print("programtokens", list(tokens))
    createtree(newtree, tree, nodelist)

    typedict = {}
    for token in tokens:
        token_type = str(type(token))[:-2].split(".")[-1]
        token_value = token.value
        if token_value not in typedict:
            typedict[token_value] = token_type
        else:
            if typedict[token_value] != token_type:
                print('!!!!!!!!')
    traversal(newtree,typedict)
    return newtree



def getNodenum(root):
    if root is None:
        return 0
    elif root.is_leaf:
        return 1
    else:
        res = 1
        for ch in root.children:
            res += getNodenum(ch)
        return res



def Treematch(tree1, tree2):
    """
    计算共同节点数
    """
    if tree1 is None or tree2 is None:
        return 0

    token1 = tree1.__dict__['token']
    token2 = tree2.__dict__['token']
    if token1 != token2:
        return 0

    ch_a = [x for x in tree1.children]
    ch_b = [x for x in tree2.children]
    m = len(ch_a)
    n = len(ch_b)
    # 动态规划计算最大匹配节点数
    res_m = [[0 for j in range(n + 1)] for i in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            res_m[i][j] = max(
                res_m[i - 1][j], res_m[i][j - 1],
                res_m[i - 1][j - 1] + Treematch(ch_a[i - 1], ch_b[j - 1]))
    return res_m[m][n] + 1


def Treediff(f1,f2):
    file1 = open(f1)
    file2 = open(f2)
    tree1, tree2 = Buildast(file1), Buildast(file2)
    file1.close()
    file2.close()
    commonnodes = Treematch(tree1, tree2)

    similarity = commonnodes / ((getNodenum(tree1) + getNodenum(tree2)) - commonnodes)

    return 1-similarity#, size

def cut_df(df, n):  
    df_num = len(df)
    every_epoch_num = math.floor((df_num/n))
    df_split = []
    for index in range(n):
        if index < n-1:
            df_tem = df[every_epoch_num * index: every_epoch_num * (index + 1)]
        else:
            df_tem = df[every_epoch_num * index:]
        df_split.append(df_tem)
    return df_split

def createfunctionfile(id,filename,s,e):
    temppath = '/bdata2/wyk/BigClone/tempdir/'
    if os.path.exists(temppath+str(id)+'.java'):
        return
    else:
        with open(temppath+str(id)+'.java','w') as f1:
            with open(filename,'r') as f2:
                oldlines = f2.readlines()[s-1:e]
                for line in oldlines:
                    f1.writelines(line)
            
    

def get_sim(dataframe):
    sim = []
    for _,pair in dataframe.iterrows():
        id1,id2 = pair.FunID1,pair.FunID2
        try:
            list1 = mappairs[mappairs['idx']==id1].values.tolist()[0]
            list2 = mappairs[mappairs['idx']==id2].values.tolist()[0]
            filename1 = list1[1]
            filename2 = list2[1]
            s1 = list1[2]
            s2 = list2[2]
            e1 = list1[3]
            e2 = list2[3]
            if abs((e1-s1+1)-(e2-s2+1))/min((e1-s1+1),(e2-s2+1)) >= 1:
                similarity = -1
            else:
                createfunctionfile(id1,filename1,s1,e1)
                createfunctionfile(id2,filename2,s2,e2)
                sourcefile1 = '/bdata2/wyk/BigClone/tempdir/' + str(id1) +'.java'   
                sourcefile2 = '/bdata2/wyk/BigClone/tempdir/' + str(id2) +'.java'   
                similarity = Treediff(sourcefile1, sourcefile2)
        except:
            similarity = -1
        sim.append(round(similarity,4))           
    return sim

if __name__== '__main__':
    start = time.time()
    mappairs = pd.read_csv('/bdata2/yyh/LVMapper_Java/allFunctionMap.csv',header=None,error_bad_lines=False)
    mappairs.columns = ['idx','filename','start','end']
    diff_list =[]
    pairs = pd.read_csv('/bdata2/wyk/analysis/sample1000w.csv',header = 0)
    end = time.time()
    print(round(end-start,4))
    pairs = pairs.loc[1000000:10000000]
    print(len(pairs))
    pool_num = 60
    df_split = cut_df(pairs,pool_num)
    pool = mp.Pool(processes=pool_num)
    start = time.time()
    it_diff = pool.imap(get_sim,df_split)
    for item in it_diff:
        diff_list += item
    pool.close()
    pool.join()
    pairs['treendiff'] = diff_list
    pairs.to_csv('/bdata2/wyk/analysis/1000wtreediff100.csv',index=0)
    end = time.time()
    print(round(end-start,4))
