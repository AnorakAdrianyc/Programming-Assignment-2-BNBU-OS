/****************************************************************************
 *                                                                          *
 * Author		: Lam Yuk Cho Adrian                                                   *
 *                                                                          *
 * Student ID	: v530000086                                                         *
 *                                                                          *
 * Date			: 4/19                                           			    *
 *                                                         					*
 * Purpose		: Programming Assignment 2                                                           *
 *                                                         					*
 ****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct record{
	char name[20];
	int score;
	struct record *next;
	
} Node; 
Node* createList(char fileName[]);
Node* insertARecord(Node *pHead);
Node* deleteARecord(Node *pHead);
Node* saveLinkedList(Node* pHead, char fileName[20]);
void printLinkedList(Node* pHead);

int main(int argc, char *argv[])
{
	Node *pHead;
	//create a linked list using the info from record.txt, return the head pointer
    //It is assumed that the info is sorted descently in scores. 
	pHead = createList("record.txt");
	printLinkedList(pHead);

	printf("choose operation(i: insert, d: delete, q: exit): ");
	char ch = getchar();
	while (ch != 'q'){
	
		if (ch == 'i')
			pHead = insertARecord(pHead); //insert a record of a student if info of this student does not exist. The the new head pointer if the new record is inserted as the first.
		if (ch == 'd')
			pHead = deleteARecord(pHead); //delete a record of a student of info of this student exist. The the new head pointer if the original head was deleted.
	    printLinkedList(pHead);
		
		printf("choose operation(i: insert, d: delete, q: exit): ");
		getchar();
		ch = getchar();
    }
	//save the records in the list pointed by pHead into a file again
    saveLinkedList(pHead, "new_record.txt");

	return 0;
}


Node* createList(char fileName[])
{
	FILE *fp;
	Node stuRecord;
	Node *pNewRecord, *pNode, *pHead = NULL;
	fp = fopen(fileName, "r");
	if (fp == NULL) {
		printf("[DEBUG] createList: failed to open %s\n", fileName);
		return NULL;
	}
	printf("[DEBUG] createList: loading records from %s\n", fileName);
	while (fscanf(fp, "%s%d", stuRecord.name, &stuRecord.score) != EOF){
		pNewRecord =(Node*)malloc(sizeof(Node));
		strcpy(pNewRecord -> name, stuRecord.name);
		pNewRecord -> score = stuRecord.score;
		pNewRecord -> next = NULL; //After all the nodes are added, the next of the end node should be NULL to indicate that this is the last one, no node after it.
		printf("[DEBUG] createList: read %s %d\n", pNewRecord->name, pNewRecord->score);
		
		// if the list is empty, pNewRecord will be the first node in the list
		if (pHead == NULL)
			pHead = pNewRecord;
		else //otherwise, add pNewRecord to the end of the list.
			pNode -> next = pNewRecord;
        pNode = pNewRecord;    //Each time after a new node is added to the list, pNode should be changed to pointed to the end node.
    }
 	fclose(fp);
    return pHead;

}
void printLinkedList(Node* pHead)
{
	Node *pNode = pHead;
	printf("[DEBUG] printLinkedList: begin\n");
	while (pNode != NULL){
		printf("%s%d\n", pNode -> name, pNode -> score);
		pNode = pNode -> next;
	}
	printf("[DEBUG] printLinkedList: end\n");
	return;
}
Node* insertARecord(Node *pHead)
{
	//enter name and score
	Node *pNewRecord;
	Node *pNode1 = pHead, *pNode2;

	pNewRecord = (Node*)malloc(sizeof(Node));
	printf("Please enter a record of a student(name, score):");
	scanf("%s%d", pNewRecord -> name, &pNewRecord -> score);
	printf("[DEBUG] insertARecord: requested insert %s %d\n",
	       pNewRecord->name, pNewRecord->score);
	pNewRecord -> next = NULL;

	if (pNode1 == NULL) {
		printf("[DEBUG] insertARecord: list empty, inserted as head\n");
		return pNewRecord;
	}
	
	//search the list to find the proper place to put the record
	while(pNode1 != NULL && pNode1 -> score > pNewRecord -> score){
		if (strcmp(pNode1 -> name, pNewRecord -> name) == 0){
			printf("Name Exist\n");
			printf("[DEBUG] insertARecord: duplicate name %s, skipping\n", pNewRecord->name);
			free(pNewRecord);
			return pHead;
		}
		pNode2 = pNode1; //record the current node before pNode1 points to the next
		pNode1 = pNode1 -> next;
	}
    
	if (pNode1 == pHead){ //for the case pHead -> score < pNewRecord -> score
		pNewRecord -> next = pHead;
		pHead = pNewRecord;
		printf("[DEBUG] insertARecord: inserted %s at head\n", pNewRecord->name);
	}
	else {//for the cases pNode1 == NULL or pNode1 -> score < pNewRecord -> score < pNode2 -> score
		pNode2 -> next = pNewRecord;
	    pNewRecord -> next = pNode1;	
		printf("[DEBUG] insertARecord: inserted %s after %s\n", pNewRecord->name, pNode2->name);
	}
	
	return pHead;

}
Node* deleteARecord(Node *pHead)
{
	char name[20];
	Node *pNode1 = pHead, *pNode2;
	printf("Please enter a name of a student to delete:");
	scanf("%s", name);
	printf("[DEBUG] deleteARecord: requested delete %s\n", name);
    while(pNode1 != NULL && strcmp(pNode1 -> name, name)!= 0){
		pNode2 = pNode1;
		pNode1 = pNode1 -> next;
	}
	if (pNode1 == NULL) {
		printf("[DEBUG] deleteARecord: name not found: %s\n", name);
		return pHead;
	}
	
	if (pNode1 == pHead) //for the case that head's name is name
	    pHead = pNode1 -> next; //the second node will be the head
	else //pNode1 -> name is name
		pNode2 -> next = pNode1 -> next;
    
	free(pNode1); //free the memory for original head
	printf("[DEBUG] deleteARecord: deleted %s\n", name);
	return pHead;
}
Node* saveLinkedList(Node* pHead, char fileName[20])
{
    Node *pNode = pHead;
    FILE *fp;

	fp = fopen(fileName, "w");
	if (fp == NULL) {
		printf("[DEBUG] saveLinkedList: failed to open %s for writing\n", fileName);
		return NULL;
	}
	printf("[DEBUG] saveLinkedList: writing to %s\n", fileName);
	
	while (pNode != NULL){
		printf("[DEBUG] saveLinkedList: wrote %s %d\n", pNode->name, pNode->score);
		fprintf(fp, "%s%d\n", pNode -> name, pNode -> score);
		pNode = pNode -> next;
	}
	
	fclose(fp);
	return 0;
}


