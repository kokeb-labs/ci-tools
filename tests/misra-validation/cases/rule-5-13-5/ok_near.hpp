// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_5_13_5_OK_NEAR_HPP
#define KV_RULE_5_13_5_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_5_13_5::near {

inline std::uint64_t unsigned_long() { return 5UL; }
inline std::int64_t long_long() { return 6LL; }
inline std::uint32_t plain_unsigned() { return 7U; }

}  // namespace kv::rule_5_13_5::near

#endif  // KV_RULE_5_13_5_OK_NEAR_HPP
