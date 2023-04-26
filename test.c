#include<stdio.h>
//这是编译器project的测试C代码
int main(int argc, char** argv){
	printf("hello world!");
	int a = 9999; //赋值操作
	int b = a + 1;
	b = - 6;
	int include; 
	if(a==b){
		return 0;
	}
	printf("%d\n",b);
	const double PI = 3.1415926;
	float d = -999.;
	float e = .12;
	printf("%f\n%f\n",d,e);
	b ++;
	char c = '\a';
	a>>1;
	a>=b;
	b+=a;
	b =0;
	/* test
	teest
	
	stet
	打印结果 */
	printf("%d", a + b);
	return 0;
}
