# List of cases for 1D WRAP

Source: <https://developer.arm.com/documentation/102482/0000/DMAC-operation/DMAC-operation-basic-commands/List-of-cases-for-1D-WRAP>

### List of cases for 1D WRAP

The 1D WRAP transfers can result in the following cases:

SRCXSIZE == 0, DESXSIZE == 0
:   The DMAC transfer does not start. Possibly only waiting for a trigger.

SRCXSIZE == 0, DESXSIZE > 0
:   The following options can be selected for the wrap type:

- continue, wrap – Nothing happens, no read or write operation occurs.
- fill – The destination is filled with the predefined fill value, so only writes occur.

SRCXSIZE > 0, DESXSIZE == 0
:   The following options can be selected for the wrap type:

continue, wrap, fill – no writes occur, only SRCXSIZE number of read transfers are sent by the DMAC. Possibly used with streaming interface to read data and pushed out on the stream output.

SRCXSIZE == DESXSIZE
:   Essentially a normal 1D operation regardless of the XTYPE setting.

SRCXSIZE > DESXSIZE
:   The following options can be selected for the wrap type:

continue, wrap, fill – The destination does not have enough room to contain the source memory content, so the copy is stopped when the destination range is filled. No overwrites happen. Excessive data is dropped within the DMAC.

SRCXSIZE < DESXSIZE
:   The following options can be selected:

    - continue – When the source runs out of data the DMAC stops copying data. SRCXSIZE number of reads and writes are executed.
    - wrap – When the end of the source data is reached, the source address counter jumps back to the original start address and the starts copying the same source data to all necessary destination memory locations. The source memory location is read multiple times during the complete wrap operation, so the source data needs to remain the same throughout the operation. This is not true when using the stream interface. Essentially, DESXSIZE number of reads and writes are executed even though SRCXSIZE is smaller. The state of the SRCXSIZE and SRCADDR in itself cannot be used to check the number of reads already executed by the DMAC. It can only be calculated from the DESXSIZE and DESADDR where the operation stands.
    - fill – A fill value is inserted to every remaining destination location. The fill value is defined in an extra register and the transfer size portion of it is used. The number of reads are equal to the SRCXSIZE, the fill value is generated within the DMAC and it creates DESXSIZE number of writes in total.

DESXADDRINC = 0
:   Results in a special case of wrapping. This setting shows that the destination address is not incremented, possibly because of targeting a FIFO, so no real wrapping can occur.

    - continue – When the source runs out of data the DMAC stops copying data. SRCXSIZE number of reads and writes are executed.
    - wrap – Since the destination address is not incremented, the source data is copied to the destination FIFO multiple times depending on the ratio of the SRCXSIZE and DESXSIZE values. The source data is read multiple times and the data is repeated in the destination FIFO. If SRCXSIZE is 3 and DESXSIZE is 8, the destination FIFO data looks like the following:

      - des\_data[0]=src\_data[0]
      - des\_data[1]=src\_data[1]
      - des\_data[2]=src\_data[2]
      - des\_data[3]=src\_data[0]
      - des\_data[4]=src\_data[1]
      - des\_data[5]=src\_data[2]
      - des\_data[6]=src\_data[0]
      - des\_data[7]=src\_data[1]
    - fill – The fill value is copied to the FIFO at the end of the transfer.
