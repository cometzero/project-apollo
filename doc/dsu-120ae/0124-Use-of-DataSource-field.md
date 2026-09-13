# Use of DataSource field

Source: <https://developer.arm.com/documentation/107721/0001/CHI-requester-interface/Use-of-DataSource-field>

### Use of DataSource field

Some CHI responses from the interconnect include a DataSource field indicating where the data was supplied from. When making use of the DataSource field, Arm® recommends providing this information as accurately as possible.

You can use the recommended encodings in the table Suggested DataSource value encodings provided in the  [AMBA® CHI Architecture Specification](https://developer.arm.com/documentation/ihi0050/latest/).

The value of this field is used to calculate some Performance Monitoring Unit (PMU) events, and can also be used by some cores to tune the performance of their data prefetchers.
