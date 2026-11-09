// Near misses (near): an explicit conversion of a scoped enumerator with a fixed type.
#ifndef KV_RULE_10_2_3_OK_NEAR_HPP
#define KV_RULE_10_2_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_10_2_3::ok_near {

enum class Channel : std::uint8_t { kLeft, kRight };

inline std::uint32_t index_of(Channel c) { return static_cast<std::uint32_t>(static_cast<std::uint8_t>(c)); }

enum Plain { kOff, kOn };

inline bool is_on(Plain p) { return p == kOn; }

}  // namespace kv::rule_10_2_3::ok_near

#endif  // KV_RULE_10_2_3_OK_NEAR_HPP
