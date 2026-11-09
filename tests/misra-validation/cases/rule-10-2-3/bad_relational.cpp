// Seeded violation (relational): an untyped unscoped enumerator compared with a plain integer.
#include <cstdint>

namespace kv::rule_10_2_3::bad_relational {

enum Level { kLow, kHigh };

bool above(Level l, std::int32_t v) { return l > v; }

}  // namespace kv::rule_10_2_3::bad_relational
