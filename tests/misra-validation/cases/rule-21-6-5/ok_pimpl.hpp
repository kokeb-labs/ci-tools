// Compliant near miss: a forward-declared implementation, complete before the owner destroys it.
#ifndef KV_RULE_21_6_5_OK_PIMPL_HPP
#define KV_RULE_21_6_5_OK_PIMPL_HPP

#include <cstdint>
#include <memory>

namespace kv::rule_21_6_5::ok_pimpl {

class Widget {
 public:
  Widget();
  ~Widget();
  Widget(const Widget&) = delete;
  Widget& operator=(const Widget&) = delete;
  Widget(Widget&&) = delete;
  Widget& operator=(Widget&&) = delete;
  [[nodiscard]] std::int32_t value() const;

 private:
  struct Impl;
  std::unique_ptr<Impl> impl_;
};

struct Widget::Impl {
  std::int32_t value{3};
};

inline Widget::Widget() = default;
inline Widget::~Widget() = default;
inline std::int32_t Widget::value() const { return (impl_ != nullptr) ? impl_->value : 0; }

}  // namespace kv::rule_21_6_5::ok_pimpl

#endif  // KV_RULE_21_6_5_OK_PIMPL_HPP
