// Seeded violation: a handle class deletes its forward-declared implementation in a member function.

namespace kv::rule_21_6_5::bad_member {

class Handle {
 public:
  void close();

 private:
  struct Impl;
  Impl* impl_{nullptr};
};

void Handle::close() {
  delete impl_;  // seeded
  impl_ = nullptr;
}

}  // namespace kv::rule_21_6_5::bad_member
