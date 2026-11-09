// Compliant near miss: a stream member repositioned between the read and the write.
#ifndef KV_RULE_30_0_2_MEMBER_OK_HPP
#define KV_RULE_30_0_2_MEMBER_OK_HPP

#include <fstream>

namespace kv::rule_30_0_2_member::ok {

class Store {
 public:
  explicit Store(std::fstream& file) : file_(file) {}
  void touch() {
    char c{};
    file_ >> c;
    static_cast<void>(file_.seekp(0, std::ios::cur));
    file_ << c;
  }

 private:
  std::fstream& file_;
};

}  // namespace kv::rule_30_0_2_member::ok

#endif  // KV_RULE_30_0_2_MEMBER_OK_HPP
