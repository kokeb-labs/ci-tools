// Near misses (near): the same base on two paths, both non-virtual.
#ifndef KV_RULE_13_1_2_OK_NEAR_HPP
#define KV_RULE_13_1_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_13_1_2::ok_near {

struct Base {
  std::uint32_t tag = 0U;
};

struct Left : Base {};
struct Right : Base {};
struct Both : Left, Right {};

inline std::uint32_t tags(const Both& b) { return static_cast<const Left&>(b).tag | static_cast<const Right&>(b).tag; }

}  // namespace kv::rule_13_1_2::ok_near

#endif  // KV_RULE_13_1_2_OK_NEAR_HPP
