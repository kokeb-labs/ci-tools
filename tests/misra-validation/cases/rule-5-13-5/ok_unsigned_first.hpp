// Near misses: suffixes that start with u; a lower-case l later in the suffix is not the first character.
#ifndef KV_RULE_5_13_5_OK_UNSIGNED_FIRST_HPP
#define KV_RULE_5_13_5_OK_UNSIGNED_FIRST_HPP

#include <cstdint>

namespace kv::rule_5_13_5::unsigned_first {

inline std::uint64_t unsigned_long() { return 5ul; }
inline std::uint64_t unsigned_long_long() { return 2Ull; }

}  // namespace kv::rule_5_13_5::unsigned_first

#endif  // KV_RULE_5_13_5_OK_UNSIGNED_FIRST_HPP
