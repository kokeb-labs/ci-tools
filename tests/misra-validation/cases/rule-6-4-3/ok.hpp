#ifndef KV_RULE_6_4_3_OK_HPP
#define KV_RULE_6_4_3_OK_HPP

// Compliant: the member of the dependent base is named through this->.
#include <cstdint>

namespace kv::rule_6_4_3::ok {

inline std::int32_t gain() { return 1; }

template <typename T>
struct Base {
  std::int32_t gain() const { return 2; }
};

template <typename T>
struct Channel : Base<T> {
  std::int32_t scaled() const { return this->gain(); }
  std::int32_t global() const { return ok::gain(); }
};

inline bool use() { return Channel<std::int32_t>{}.scaled() == Channel<std::int32_t>{}.global(); }

}  // namespace kv::rule_6_4_3::ok

#endif  // KV_RULE_6_4_3_OK_HPP
