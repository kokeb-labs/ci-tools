// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_4_3_OK_NEAR_HPP
#define KV_RULE_6_4_3_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_6_4_3::near {

template <typename T>
struct Store {
  std::int32_t offset() const { return 20; }
};
// The dependent base's member named with Base<T>:: qualification.
template <typename T>
struct View : Store<T> {
  std::int32_t at() const { return Store<T>::offset(); }
};
inline std::int32_t use_view() { return View<std::int16_t>{}.at(); }

}  // namespace kv::rule_6_4_3::near

#endif  // KV_RULE_6_4_3_OK_NEAR_HPP
