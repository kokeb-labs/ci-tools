// Seeded violation: errno set to an error number by our own code.
#include <cerrno>

namespace kv::rule_22_4_1::bad {

void report_busy() { errno = EBUSY; }

}  // namespace kv::rule_22_4_1::bad
