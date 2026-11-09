// Seeded violation (anonymous): an anonymous unscoped enumeration used for constants.
#include <cstdint>

namespace kv::rule_10_2_2::bad_anonymous {

enum : std::uint8_t { kMaxRetries = 3 };

std::int32_t retries() { return kMaxRetries; }

}  // namespace kv::rule_10_2_2::bad_anonymous
